#!/usr/bin/env python3
"""
downgrade_sources.py — Ricostruisce i sorgenti del portfolio dagli ORIGINALI
non-glazati, riducendone la qualità (lato lungo massimo) per protezione anti-AI.

Deciso: Glaze/Nightshade scartati (non bloccano GPT-4o), si va di riduzione
qualità + sistemi non-perturbativi (watermark, robots.txt, meta noai).

Mapping (stesso di apply_glaze.py): portfolioN -> <sezione>/<slug>/NN_page.jpg.
portfolio9 non è usato nel sito.

Uso:
  python downgrade_sources.py --dry-run            # mostra cosa farebbe
  python downgrade_sources.py --max-size 800       # riduci a lato lungo 800
  python downgrade_sources.py [--originals-dir assets/originals]
"""

import argparse
import ast
import sys
from pathlib import Path

from PIL import Image

PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Mapping definito in apply_glaze.py (riusato qui per coerenza)
_glaze = (PROJECT_ROOT / "scripts" / "apply_glaze.py").read_text()
MAPPING = {}
for node in ast.parse(_glaze).body:
    if isinstance(node, ast.Assign):
        for t in node.targets:
            if isinstance(t, ast.Name) and t.id == "MAPPING":
                MAPPING = ast.literal_eval(node.value)


def downgrade(src_path: Path, dest_path: Path, max_size: int) -> str:
    """Apre src, riduce il lato lungo a max_size, salva su dest (JPEG q85)."""
    with Image.open(src_path) as im:
        im = im.convert("RGB")
        im.thumbnail((max_size, max_size), Image.LANCZOS)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        im.save(dest_path, "JPEG", quality=85, optimize=True)
    return f"{im.size[0]}x{im.size[1]}"


def main():
    ap = argparse.ArgumentParser(description=(
        "Riduce i sorgenti del portfolio dagli originali non-glazati."))
    ap.add_argument("--dry-run", action="store_true",
                    help="mostra cosa farebbe senza modificare nulla")
    ap.add_argument("--max-size", type=int, default=800,
                    help="lato lungo massimo in px (default 800)")
    ap.add_argument("--originals-dir", default="assets/originals",
                    help="dir con gli originali NON-glazati")
    args = ap.parse_args()

    orig_dir = PROJECT_ROOT / args.originals_dir
    done, missing = [], []

    print(f"=== {'DRY-RUN' if args.dry_run else 'APPLICAZIONE'} ===")
    print(f"Origine:       {orig_dir}")
    print(f"Lato lungo max: {args.max_size}px")

    for src_name, rel in sorted(MAPPING.items(),
                                key=lambda kv: (len(kv[0]), kv[0])):
        src = orig_dir / f"{src_name}.jpg"
        dest = PROJECT_ROOT / "assets" / "portfolio" / rel

        if not src.exists():
            missing.append((src_name, rel, "originale assente"))
            continue
        if args.dry_run:
            done.append((src_name, rel, "da ridurre"))
            continue
        try:
            dims = downgrade(src, dest, args.max_size)
            done.append((src_name, rel, dims))
        except Exception as e:  # noqa: BLE001
            missing.append((src_name, rel, f"ERRORE {e}"))

    print(f"\n[{len(done)}] sorgenti {('DA RIDURRE' if args.dry_run else 'RIDOTTI a <=%spx' % args.max_size)}:")
    for src, rel, info in done:
        print(f"  {src:12} -> assets/portfolio/{rel}   {info}")

    if missing:
        print(f"\n[PROBLEMI] {len(missing)}:")
        for src, rel, why in missing:
            print(f"  {src:12} -> {rel}  ({why})")
        if not args.dry_run:
            sys.exit(2)

    if args.dry_run:
        print("\n(DRY-RUN: nulla è stato modificato.)")


if __name__ == "__main__":
    main()
