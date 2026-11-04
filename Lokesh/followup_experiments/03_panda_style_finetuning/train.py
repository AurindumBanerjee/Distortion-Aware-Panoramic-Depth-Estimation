#!/usr/bin/env python3
"""Unlabeled teacher/student pseudo-label training.

Teacher: frozen DA360. Student: small U-Net. Training sees RGB + teacher pseudo
disparity only; GT depth is not read during the optimization stage.
Augmentations are spherical yaw rolls and horizontal reflection. The patch-
normalized objective is PanDA-inspired, not an exact PanDA reproduction.
"""
from __future__ import annotations
import argparse, csv, json, os, random, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from torch import nn
from torch.utils.data import Dataset, DataLoader
from common import ROOT, environment_info, load_config, load_model, prepare_output, save_json, seed_everything
from student_model import StudentDepthNet


def read_rgb_list(cfg):
    root = Path(cfg["dataset"]["root"])
    if not root.is_absolute():
        root = (ROOT / root).resolve()
    list_path = root / cfg["dataset"].get("list", "test.txt")
    if not list_path.exists():
        raise FileNotFoundError(list_path)
    items = []
    for line in list_path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        rel = line.split()[0]
        parts = Path(rel).parts
        sid = f"{parts[0]}_{Path(rel).stem}" if len(parts) > 2 else Path(rel).stem
        # PanoX directory names are the independent environment clusters.
        group = parts[0] if len(parts) > 2 else sid
        items.append((sid, group, root / rel))
    cap = cfg["dataset"].get("max_images")
    return items[:int(cap)] if cap else items


def resize_rgb(path, height, width):
    image = cv2.imread(str(path), cv2.IMREAD_COLOR)
    if image is None:
        raise IOError(f"Could not read RGB: {path}")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    interp = cv2.INTER_AREA if image.shape[0] > height else cv2.INTER_CUBIC
    return cv2.resize(image, (width, height), interpolation=interp)


def make_cache(cfg, items, groups_train, out):
    cache = out / "pseudo_cache"
    cache.mkdir(parents=True, exist_ok=True)
    teacher = load_model(cfg["teacher"])
    h, w = int(cfg["dataset"]["height"]), int(cfg["dataset"]["width"])
    for i, (sid, group, path) in enumerate(items):
        if group not in groups_train:
            continue
        dest = cache / f"{sid}.npz"
        if dest.exists() and cfg["training"].get("cache_teacher_predictions", True):
            continue
        rgb = resize_rgb(path, h, w)
        pred = teacher.predict(rgb, kind="erp").astype(np.float32)
        ok = np.isfinite(pred) & (pred > 0)
        if ok.sum() < 100:
            raise RuntimeError(f"Teacher produced too few valid pixels for {sid}")
        med = float(np.median(pred[ok]))
        mad = float(np.mean(np.abs(pred[ok] - med))) + 1e-6
        target = (pred - med) / mad
        target[~ok] = 0.0
        np.savez_compressed(dest, rgb=rgb, target=target.astype(np.float32), valid=ok.astype(np.uint8))
        if (i + 1) % 10 == 0 or i + 1 == len(items):
            print(f"Pseudo-label cache {i+1}/{len(items)}: {sid}")
    del teacher
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    return cache


class PseudoCache(Dataset):
    def __init__(self, items, cache, train: bool):
        self.items = items
        self.cache = cache
        self.train = train
    def __len__(self):
        return len(self.items)
    def __getitem__(self, index):
        sid = self.items[index][0]
        z = np.load(self.cache / f"{sid}.npz")
        rgb = z["rgb"].astype(np.float32) / 255.0
        target = z["target"].astype(np.float32)
        valid = z["valid"].astype(bool)
        if self.train:
            if random.random() < 0.8:
                shift = random.randrange(rgb.shape[1])
                rgb, target, valid = (np.roll(x, shift, axis=1) for x in (rgb, target, valid))
            if random.random() < 0.5:
                rgb, target, valid = (np.flip(x, axis=1).copy() for x in (rgb, target, valid))
        return (torch.from_numpy(rgb.transpose(2, 0, 1).copy()).float(),
                torch.from_numpy(target[None].copy()).float(),
                torch.from_numpy(valid[None].copy()).float())


def patch_normalize(x, grid):
    h, w = x.shape[-2:]
    kh, kw = max(1, h // grid), max(1, w // grid)
    mu = F.avg_pool2d(x, (kh, kw), stride=(kh, kw))
    second = F.avg_pool2d(x * x, (kh, kw), stride=(kh, kw))
    mu = F.interpolate(mu, size=(h, w), mode="nearest")
    var = F.interpolate((second - F.avg_pool2d(x, (kh, kw), stride=(kh, kw)).pow(2)).clamp_min(1e-5),
                        size=(h, w), mode="nearest")
    return (x - mu) / torch.sqrt(var + 1e-4)


def gradient_loss(pred, target, valid):
    dxp, dyp = pred[..., :, 1:] - pred[..., :, :-1], pred[..., 1:, :] - pred[..., :-1, :]
    dxt, dyt = target[..., :, 1:] - target[..., :, :-1], target[..., 1:, :] - target[..., :-1, :]
    mx = valid[..., :, 1:] * valid[..., :, :-1]
    my = valid[..., 1:, :] * valid[..., :-1, :]
    lx = ((dxp - dxt).abs() * mx).sum() / mx.sum().clamp_min(1)
    ly = ((dyp - dyt).abs() * my).sum() / my.sum().clamp_min(1)
    return lx + ly


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=str(HERE / "config.yaml"))
    ap.add_argument("--set", action="append", default=[])
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    cfg = load_config(a.config, a.set)
    seed_everything(int(cfg.get("seed", 0)))
    if not torch.cuda.is_available():
        raise SystemExit("CUDA required. Enable both Kaggle T4 GPUs for student training.")
    items = read_rgb_list(cfg)
    # Deterministic environment split; no GT is opened or used in this file.
    envs = sorted({x[1] for x in items})
    rng = random.Random(int(cfg.get("seed", 0)))
    rng.shuffle(envs)
    n_train = max(1, min(len(envs) - 1, round(len(envs) * float(cfg["training"]["train_group_fraction"]))))
    train_envs, val_envs = set(envs[:n_train]), set(envs[n_train:])
    train_items = [x for x in items if x[1] in train_envs]
    val_items = [x for x in items if x[1] in val_envs]
    out = prepare_output(cfg["output_dir"] + "/run_" + time.strftime("%Y%m%d_%H%M%S"), a.overwrite)
    save_json(out / "config_environment.json", {"config": cfg, "environment": environment_info(),
              "train_environments": sorted(train_envs), "validation_environments": sorted(val_envs),
              "optimization_uses_ground_truth": False})
    print(f"Environments: {len(envs)} | train: {sorted(train_envs)} | validation: {sorted(val_envs)}")
    cache = make_cache(cfg, items, train_envs | val_envs, out)
    train_ds, val_ds = PseudoCache(train_items, cache, True), PseudoCache(val_items, cache, False)
    tc = cfg["training"]
    train_loader = DataLoader(train_ds, batch_size=int(tc["batch_size"]), shuffle=True,
                              num_workers=int(tc.get("workers", 4)), pin_memory=True, drop_last=False)
    val_loader = DataLoader(val_ds, batch_size=int(tc["batch_size"]), shuffle=False,
                            num_workers=int(tc.get("workers", 4)), pin_memory=True)
    net = StudentDepthNet().cuda()
    if torch.cuda.device_count() > 1:
        net = nn.DataParallel(net)
    opt = torch.optim.AdamW(net.parameters(), lr=float(tc["learning_rate"]),
                            weight_decay=float(tc.get("weight_decay", 1e-5)))
    scaler = torch.amp.GradScaler("cuda", enabled=bool(tc.get("amp", True)))
    grid = int(tc.get("patch_grid", 8))
    grad_w = float(tc.get("gradient_loss_weight", 0.1))
    patch_w = float(tc.get("patch_normalization_weight", 0.5))
    best = float("inf")
    history = []
    for epoch in range(1, int(tc["epochs"]) + 1):
        net.train()
        losses = []
        for rgb, target, valid in train_loader:
            rgb, target, valid = rgb.cuda(non_blocking=True), target.cuda(non_blocking=True), valid.cuda(non_blocking=True)
            opt.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=bool(tc.get("amp", True))):
                pred = net(rgb)
                base = (F.smooth_l1_loss(pred * valid, target * valid, reduction="sum") /
                        valid.sum().clamp_min(1))
                pn = F.smooth_l1_loss(patch_normalize(pred, grid) * valid,
                                       patch_normalize(target, grid) * valid, reduction="sum") / valid.sum().clamp_min(1)
                gl = gradient_loss(pred, target, valid)
                loss = base + patch_w * pn + grad_w * gl
            scaler.scale(loss).backward()
            scaler.step(opt)
            scaler.update()
            losses.append(float(loss.detach().cpu()))
        net.eval()
        val_losses = []
        with torch.no_grad():
            for rgb, target, valid in val_loader:
                rgb, target, valid = rgb.cuda(), target.cuda(), valid.cuda()
                with torch.amp.autocast("cuda", enabled=bool(tc.get("amp", True))):
                    pred = net(rgb)
                    v = F.smooth_l1_loss(pred * valid, target * valid, reduction="sum") / valid.sum().clamp_min(1)
                val_losses.append(float(v.cpu()))
        tr, va = float(np.mean(losses)), float(np.mean(val_losses))
        history.append({"epoch": epoch, "train_loss": tr, "validation_loss": va})
        print(f"epoch {epoch:02d}/{tc['epochs']} train={tr:.5f} val={va:.5f}")
        state = net.module.state_dict() if isinstance(net, nn.DataParallel) else net.state_dict()
        torch.save({"state_dict": state, "epoch": epoch, "config": cfg}, out / "last.pt")
        if va < best:
            best = va
            torch.save({"state_dict": state, "epoch": epoch, "config": cfg}, out / "best.pt")
        if epoch % int(tc.get("save_every", 1)) == 0:
            with (out / "history.csv").open("w", newline="", encoding="utf-8") as f:
                w = csv.DictWriter(f, fieldnames=list(history[0])); w.writeheader(); w.writerows(history)
    save_json(out / "training_summary.json", {"best_validation_loss": best, "history": history,
              "train_environments": sorted(train_envs), "validation_environments": sorted(val_envs),
              "note": "Teacher pseudo-targets only; no ground-truth depths used in optimization."})
    print("Best student:", out / "best.pt")


if __name__ == "__main__":
    main()
