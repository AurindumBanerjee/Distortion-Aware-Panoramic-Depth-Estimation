#!/usr/bin/env bash
# Move every experiment output produced so far into old_experiments/<name>/, keeping the original relative paths,
# so that the next round starts from clean result folders. Code, configs, data and weights are not touched.
#   scripts/archive_old_experiments.sh [name]      (default: v2_<date>)
# Moves: results/*, RESULTS.md, logs/, best_model/<benchmark records>, and the outputs*/ logs*/ folders of the three
# series. Run it on every machine that holds outputs (laptop and server); it only moves what exists there.
set -uo pipefail
AUR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$AUR"
NAME="${1:-v2_$(date +%Y%m%d)}"
DST="old_experiments/$NAME"
mkdir -p "$DST"
moved=0
mv_keep() {  # mv_keep <relative path>
    local src="$1"
    [ -e "$src" ] || return 0
    mkdir -p "$DST/$(dirname "$src")"
    if [ -e "$DST/$src" ]; then echo "skip (exists in archive): $src"; return 0; fi
    mv "$src" "$DST/$src" && moved=$((moved + 1))
}
shopt -s nullglob dotglob
for f in results/*; do mv_keep "$f"; done
mv_keep RESULTS.md
mv_keep logs
for d in best_model/*/; do mv_keep "${d%/}"; done
for s in 1_gradient_polar_fusion 2_mobius_tta_ensembling 3_structured3d_benchmark; do
    for d in "$s"/outputs* "$s"/logs*; do [ -d "$d" ] && mv_keep "$d"; done
done
mkdir -p results logs
cat > "$DST/README.md" <<TXT
# Archived experiments: $NAME
Moved by scripts/archive_old_experiments.sh on $(date '+%F %T'). Paths below this folder mirror the repository.
Headline conclusions of this round: results/WRITEUP_20261104.md (if present). PanoX statistics in summaries written
before 4 Nov 12:20 used the wrong clustering (80 groups instead of 8 environments); use SUMMARY_20261104_122025.md.
TXT
echo "moved $moved items into $DST"
