"""Write notebooks/kaggle_acgf.ipynb (the GPU run of the ACGF experiments on Kaggle).

    python scripts/build_kaggle_notebook.py
"""
from __future__ import annotations

import os

import nbformat as nbf

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INTRO = """# ACGF experiments on Kaggle (GPU)

Runs the comparison from `README.md` (section *ACGF*) with MiDaS DPT-Hybrid on Structured3D and Holo360D:
baseline, tangent, rotation, hybrid, the 360MonoDepth-style baseline (`mono360`) and ACGF, then the ACGF
ablations and threshold sweep on a subset. Optionally the same with DAP.

**Before running**
1. *Settings*: Accelerator = **GPU** (T4 or P100), **Internet = on** (needs a phone-verified account).
2. *Add Input*: three **private** datasets you upload once (*Datasets -> New Dataset*):
   * `dad-code`: the file `kaggle_upload/dad-code.zip`, made locally with `python scripts/package_for_kaggle.py`;
   * `holo360d`: the file `data/holo360d/holo360d.zip`;
   * `structured3d`: the file `structured3d.zip`.
   Kaggle unpacks zips on upload; the next cell finds everything under `/kaggle/input`, whatever the dataset names.
   Keep these datasets private: they contain third-party data.
3. Edit the settings cell (which datasets, image limits), then *Save Version -> Save & Run All (Commit)*. A commit
   keeps running after you close the tab (12 h limit per session). With the defaults, expect roughly 4-6 h; to stay
   well inside the limit, run `RUNS` in two sessions (e.g. Structured3D first, then Holo360D).
4. When it finishes, download **`acgf_results.zip`** from the *Output* tab, unzip it into the project folder
   (it contains `results/acgf_*`), and tell Claude it is there.
"""

SETTINGS = '''# ---- settings -------------------------------------------------------------------------------
RUNS = ["structured3d", "holo360d_indoor", "holo360d_outdoor"]   # drop entries to split across sessions
LIMIT = None            # images per split for the main comparison (None = full split); e.g. 10 for a smoke test
ABLATION_LIMIT = 40     # ACGF ablations + threshold sweep run on the first N images of each split
RUN_DAP = False         # also run ACGF with DAP (needs Internet; downloads ~1.5 GB); experimental
DAP_LIMIT = 60
'''

LOCATE = r'''import os, sys, glob, shutil, subprocess, zipfile, time
os.environ["OPENCV_IO_ENABLE_OPENEXR"] = "1"   # Holo360D depth is EXR; must be set before cv2 is imported

def find_dir(pred, root="/kaggle/input", max_depth=5):
    for base, dirs, files in os.walk(root):
        if base[len(root):].count(os.sep) > max_depth:
            dirs[:] = []
            continue
        if pred(base, dirs, files):
            return base
    return None

WORK = "/kaggle/working/dad"
code = find_dir(lambda b, d, f: "run_experiment.py" in f)
if code is None:  # zip not unpacked by Kaggle
    z = glob.glob("/kaggle/input/**/dad-code*.zip", recursive=True)
    assert z, "dad-code.zip not found: add the code dataset as an input"
    zipfile.ZipFile(z[0]).extractall(WORK)
else:
    shutil.copytree(code, WORK, dirs_exist_ok=True)
os.chdir(WORK)
sys.path.insert(0, WORK)

holo = find_dir(lambda b, d, f: "Indoor_015" in d or "Outdoor_004" in d)
s3d = find_dir(lambda b, d, f: "rgb" in d and "depth" in d and any(x.startswith("test") for x in f))
if s3d is None:
    s3d = find_dir(lambda b, d, f: "rgb" in d and "depth" in d and os.path.isdir(os.path.join(b, "rgb"))
                   and any(x.startswith("scene_") for x in os.listdir(os.path.join(b, "rgb"))[:5]))
print("code:", code, "\nholo360d:", holo, "\nstructured3d:", s3d)
os.makedirs("data", exist_ok=True)
for name, src in (("holo360d", holo), ("structured3d", s3d)):
    dst = os.path.join("data", name)
    if src is None:
        print(f"WARNING: {name} not found -- runs using it will be skipped")
        continue
    os.makedirs(dst, exist_ok=True)
    for entry in os.listdir(src):  # symlink the data folders, copy the split lists
        s_, d_ = os.path.join(src, entry), os.path.join(dst, entry)
        if os.path.lexists(d_):
            continue
        if entry.endswith(".txt"):
            shutil.copy(s_, d_)
        else:
            os.symlink(s_, d_)
    for lst in glob.glob(f"lists/{name}/*.txt"):
        shutil.copy(lst, os.path.join(dst, os.path.basename(lst)))
print(sorted(os.listdir("data/holo360d"))[:8] if holo else "", sorted(os.listdir("data/structured3d"))[:6] if s3d else "")
'''

SETUP = r'''subprocess.run("nvidia-smi", shell=True)
# The vendored MiDaS code needs timm 0.6.13; OpenEXR is a fallback reader for Holo360D depth.
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "timm==0.6.13", "OpenEXR", "tabulate"], check=True)
os.makedirs("weights", exist_ok=True)
w = "weights/dpt_hybrid_384.pt"
if not os.path.exists(w):
    subprocess.run(["wget", "-q", "-O", w, "https://github.com/isl-org/MiDaS/releases/download/v3/dpt_hybrid_384.pt"], check=True)
print(w, os.path.getsize(w) / 2**20, "MB")
'''

SANITY = r'''# Quick checks: geometry + ACGF unit tests, and that one depth file of each dataset reads correctly.
r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests/test_geometry.py", "tests/test_acgf.py"], capture_output=True, text=True)
print(r.stdout[-3000:], r.stderr[-2000:])
from datasets.panorama import PanoramaDataset
import numpy as np
if holo:
    s = PanoramaDataset("data/holo360d", "test_indoor.txt", 512, 1024, name="holo360d", limit=1)[0]
    print("holo360d", s.id, s.rgb.shape, "valid %.2f" % s.valid.mean(), "depth range", np.nanmin(s.depth), np.nanmax(s.depth))
if s3d:
    s = PanoramaDataset("data/structured3d", "test_s3250.txt", 512, 1024, name="structured3d", limit=1)[0]
    print("structured3d", s.id, s.rgb.shape, "valid %.2f" % s.valid.mean(), "depth range", np.nanmin(s.depth), np.nanmax(s.depth))
'''

RUN = r'''MAIN_TAGS = ["E1_baseline", "E2_tangent", "E3_rotation", "E4_hybrid", "E10_acgf", "E11_mono360"]
ABL_TAGS = ["E1_baseline", "E4_hybrid", "E10_acgf", "E10_acgf_ablation", "E10_acgf_threshold"]
SPLITS = {  # run name -> (config, list file, needs)
    "structured3d": ("configs/acgf_structured3d.yaml", "test_s3250.txt", s3d),
    "holo360d_indoor": ("configs/acgf_holo360d.yaml", "test_indoor.txt", holo),
    "holo360d_outdoor": ("configs/acgf_holo360d.yaml", "test_outdoor.txt", holo),
}

def run(config, out, lst, tags, limit, stages):
    cmd = [sys.executable, "run_experiment.py", "--config", config, "--stages", *stages, "--tags", *tags,
           "--set", f"dataset.list={lst}", f"output_dir={out}", f"dataset.limit={'null' if limit is None else limit}"]
    print(" ".join(cmd), flush=True)
    t = time.time()
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in p.stdout:
        print(line, end="", flush=True)
    p.wait()
    print(f"--> exit {p.returncode} after {(time.time() - t) / 60:.1f} min", flush=True)
    return p.returncode

status = {}
for name in RUNS:
    config, lst, needs = SPLITS[name]
    if needs is None:
        status[name] = "skipped (data not found)"
        continue
    out = f"results/acgf_midas_{name}"
    rc1 = run(config, out, lst, MAIN_TAGS, LIMIT, ["geometry", "main", "reports", "timing", "qualitative"])
    rc2 = run(config, out + "_ablation", lst, ABL_TAGS, ABLATION_LIMIT, ["main", "reports"])
    status[name] = (rc1, rc2)
print(status)
'''

DAP = r'''# Optional: ACGF with DAP (the target panoramic model). Experimental -- if anything fails here, the MiDaS
# results above are unaffected; send the error output along with the results.
if RUN_DAP and holo:
    if not os.path.isdir("third_party/DAP"):
        subprocess.run(["git", "clone", "--depth", "1", "https://github.com/Insta360-Research-Team/DAP", "third_party/DAP"], check=True)
    req = "third_party/DAP/requirements.txt"
    if os.path.exists(req):  # do not let DAP's pins replace Kaggle's torch
        pkgs = [l.strip() for l in open(req) if l.strip() and not l.startswith("#") and not l.lower().startswith(("torch", "numpy"))]
        subprocess.run([sys.executable, "-m", "pip", "install", "-q", *pkgs])
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "huggingface_hub"], check=True)
    from huggingface_hub import hf_hub_download
    os.makedirs("weights/dap", exist_ok=True)
    p = hf_hub_download("Insta360-Research/DAP-weights", "model.pth", local_dir="weights/dap")
    print("DAP weights:", p)
    for lst, tag in (("test_indoor.txt", "indoor"), ("test_outdoor.txt", "outdoor")):
        run("configs/acgf_dap_holo360d.yaml", f"results/acgf_dap_holo360d_{tag}", lst,
            ["E1_baseline", "E2_tangent", "E3_rotation", "E4_hybrid", "E10_acgf", "E10_acgf_ablation"], DAP_LIMIT,
            ["geometry", "main", "reports", "qualitative"])
'''

PACK = r'''# Bundle everything except raw prediction arrays into /kaggle/working/acgf_results.zip
out = "/kaggle/working/acgf_results.zip"
n = 0
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for d in sorted(glob.glob("results/acgf_*")):
        for base, dirs, files in os.walk(d):
            if os.sep + "predictions" in base + os.sep:
                continue
            for f in files:
                if f.startswith("heatmap__") and f.endswith(".npy"):
                    continue
                z.write(os.path.join(base, f))
                n += 1
print(out, n, "files", "%.1f MB" % (os.path.getsize(out) / 2**20))
'''


def main():
    nb = nbf.v4.new_notebook()
    nb.cells = [nbf.v4.new_markdown_cell(INTRO), nbf.v4.new_code_cell(SETTINGS), nbf.v4.new_code_cell(LOCATE),
                nbf.v4.new_code_cell(SETUP), nbf.v4.new_code_cell(SANITY),
                nbf.v4.new_markdown_cell("## Main comparison and ablations (MiDaS DPT-Hybrid)"), nbf.v4.new_code_cell(RUN),
                nbf.v4.new_markdown_cell("## Optional: DAP"), nbf.v4.new_code_cell(DAP),
                nbf.v4.new_markdown_cell("## Package the results (download `acgf_results.zip` from the Output tab)"),
                nbf.v4.new_code_cell(PACK)]
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    p = os.path.join(ROOT, "notebooks", "kaggle_acgf.ipynb")
    nbf.write(nb, p)
    print("wrote", p)


if __name__ == "__main__":
    main()
