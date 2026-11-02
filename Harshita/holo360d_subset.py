import argparse, os, re, collections
from huggingface_hub import HfApi
from remotezip import RemoteZip

REPO = "ouou123/Holo360D"
ap = argparse.ArgumentParser()
ap.add_argument("--sizes", action="store_true", help="print size of every test zip, nothing downloaded")
ap.add_argument("--list", action="store_true", help="print layout of the zips given in --scenes, nothing downloaded")
ap.add_argument("--scenes", nargs="*", default=["Indoor_001"])
ap.add_argument("--include", nargs="*", default=[r"\.jpg$", r"\.exr$"], help="regexes a member path must match (any)")
ap.add_argument("--exclude", nargs="*", default=["mask", "pose"], help="substrings to skip")
ap.add_argument("--every", type=int, default=15, help="keep every Nth frame")
ap.add_argument("--out", default="data/holo360d")
a = ap.parse_args()

if a.sizes:
    for e in HfApi().list_repo_tree(REPO, path_in_repo="test", repo_type="dataset"):
        print(f"{e.path:40s} {getattr(e, 'size', 0) / 2**30:8.2f} GB")
    raise SystemExit

for s in a.scenes:
    with RemoteZip(f"https://huggingface.co/datasets/{REPO}/resolve/main/test/{s}.zip") as z:
        infos = [i for i in z.infolist() if not i.is_dir()]
        if a.list:
            ext = collections.Counter(os.path.splitext(i.filename)[1] for i in infos)
            dirs = collections.Counter(os.path.dirname(i.filename) for i in infos)
            print(s, len(infos), "files", dict(ext)); print(dict(list(dirs.items())[:15]))
            for i in infos[:12]: print("  ", i.filename, round(i.file_size / 2**20, 1), "MB")
            continue
        keep = [i for i in infos if any(re.search(p, i.filename, re.I) for p in a.include)
                and not any(x in i.filename.lower() for x in a.exclude)]
        stem = lambda n: os.path.splitext(os.path.basename(n))[0]
        frames = sorted({stem(i.filename) for i in keep})[::a.every]
        sel = [i for i in keep if stem(i.filename) in set(frames)]
        print(s, len(sel), "files", round(sum(i.file_size for i in sel) / 2**30, 2), "GB")
        for i in sel: z.extract(i, os.path.join(a.out, s))