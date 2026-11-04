"""Generate the test.txt list file for the DAP NYC distance panorama dataset.

Usage:
    python scripts/make_nyc_list.py --rgb-dir <path> --depth-dir <path> --out <path> [--limit N]

The list file format expected by PanoramaDataset is:
    relative/path/to/rgb.png relative/path/to/depth.npy
"""
import argparse
import os
import re


def natural_sort_key(s):
    """Sort strings with embedded numbers in natural order (0, 1, 2, ..., 10, 11, ...)."""
    return [int(c) if c.isdigit() else c.lower() for c in re.split(r'(\d+)', s)]


def main():
    parser = argparse.ArgumentParser(description="Generate test.txt for the NYC panorama dataset")
    parser.add_argument("--rgb-dir", required=True, help="Absolute path to nyc_raw_images_panorama")
    parser.add_argument("--depth-dir", required=True, help="Absolute path to nyc_distance_panorama_npy")
    parser.add_argument("--out", required=True, help="Output directory (dataset root for the experiment)")
    parser.add_argument("--limit", type=int, default=None, help="Only include the first N pairs")
    args = parser.parse_args()

    # Discover all panorama IDs from the RGB directory
    rgb_files = [f for f in os.listdir(args.rgb_dir) if f.endswith(".png")]
    ids = sorted(
        [f.replace("panorama_", "").replace(".png", "") for f in rgb_files],
        key=natural_sort_key,
    )
    print(f"Found {len(ids)} RGB panoramas")

    # Verify matching depth files exist
    matched = []
    for pid in ids:
        depth_file = os.path.join(args.depth_dir, f"erp_distance_{pid}.npy")
        if os.path.isfile(depth_file):
            matched.append(pid)
        else:
            print(f"  WARNING: no depth for id={pid}")

    print(f"Matched RGB-depth pairs: {len(matched)}")

    if args.limit:
        matched = matched[: args.limit]
        print(f"Limited to first {args.limit} pairs")

    # Create the output directory and write the list file.
    # The list file uses paths relative to --out, so we write paths that
    # point back to the original data via symlinks or absolute-ish relative paths.
    # The simplest approach: create symlinks inside --out so paths are clean.
    os.makedirs(args.out, exist_ok=True)
    rgb_link = os.path.join(args.out, "rgb")
    depth_link = os.path.join(args.out, "depth")

    # On Windows, creating directory symlinks may need admin.  Fall back to
    # writing absolute paths directly into the list file if symlinks fail.
    use_absolute = False
    for link, target in [(rgb_link, args.rgb_dir), (depth_link, args.depth_dir)]:
        if os.path.exists(link):
            # Already exists (previous run) — leave it
            continue
        try:
            os.symlink(target, link, target_is_directory=True)
        except OSError:
            print(f"  Symlink failed for {link} -> {target}; will use absolute paths in test.txt")
            use_absolute = True
            break

    list_path = os.path.join(args.out, "test.txt")
    with open(list_path, "w") as f:
        for pid in matched:
            if use_absolute:
                rgb_path = os.path.join(args.rgb_dir, f"panorama_{pid}.png")
                depth_path = os.path.join(args.depth_dir, f"erp_distance_{pid}.npy")
            else:
                rgb_path = f"rgb/panorama_{pid}.png"
                depth_path = f"depth/erp_distance_{pid}.npy"
            f.write(f"{rgb_path} {depth_path}\n")

    print(f"Wrote {len(matched)} entries to {list_path}")


if __name__ == "__main__":
    main()
