#!/usr/bin/env python3
"""
Pipeline di ottimizzazione immagini per il portfolio Cinerea.

Da cartelle di origine produce, per ogni immagine:
  - versione "thumb" (max 600px lato lungo) in WebP → public/images/thumbnails/
  - versione "full" (max 1600px lato lungo) in WebP  → public/images/portfolio/

USO:
    python3 scripts/optimize_images.py [SRC_DIR]

SRC_DIR (opzionale) = cartella con le immagini di origine (ex: Downloads lettere originali).
Default: ./assets/originals/
Se non viene passato SRC_DIR, lavora su assets/originals/ dentro il progetto.

DIPENDENZE:
    pip install Pillow
Requisito per supporto WebP: Pillow con libwebp compilato (standard su pip recenti).

Per aggiungere nuove immagini all'artista:
  1. Mette le immagini originali in assets/originals/
  2. Lancia questo script (npm run optimize)
  3. Vengono generate thumb + full, pronte per essere referenziate nel frontmatter dei lavori.
"""

import os
import re
import sys
from pathlib import Path

from PIL import Image

# ---- Configurazione -------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_SRC = PROJECT_ROOT / "assets" / "originals"
THUMB_DIR = PROJECT_ROOT / "public" / "images" / "thumbnails"
FULL_DIR = PROJECT_ROOT / "public" / "images" / "portfolio"
OG_DIR = PROJECT_ROOT / "public" / "images" / "og"

# Dimensioni max (lato lungo) in px
THUMB_MAX = 600
FULL_MAX = 1600

# Qualità WebP (80-85 è il sweet spot per illustrazioni)
WEBP_QUALITY = 82

ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}

# ---- Helpers --------------------------------------------------------
def slugify(filename: str) -> str:
    """Converte nome file in slug URL-safe."""
    base = Path(filename).stem.lower()
    base = re.sub(r"[^a-z0-9]+", "-", base)
    base = base.strip("-")
    return base or "image"


def sanitize_name(name: str) -> str:
    """Rimuove eventuali prefissi numerici tipo '123_immagine'."""
    return name


def process_image(src: Path) -> bool:
    """Elabora una singola immagine, salva thumb + full WebP. Ritorna True se ok."""
    slug = slugify(src.name)

    try:
        with Image.open(src) as im:
            # Conversione in RGB (con alpha → RGBA per WebP). WebP supporta alpha.
            if im.mode in ("RGBA", "LA"):
                im = im.convert("RGBA")
            else:
                im = im.convert("RGB")

            # ---- Versione full (1600px lato lungo) ----
            full = im.copy()
            full.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
            full_path = FULL_DIR / f"{slug}.webp"
            full.save(full_path, "WEBP", quality=WEBP_QUALITY, method=6)
            print(f"  full  -> {full_path.name} ({full_path.stat().st_size//1024} KB)")

            # ---- Versione thumb (600px lato lungo) ----
            thumb = im.copy()
            thumb.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
            thumb_path = THUMB_DIR / f"{slug}.webp"
            thumb.save(thumb_path, "WEBP", quality=WEBP_QUALITY, method=6)
            print(f"  thumb -> {thumb_path.name} ({thumb_path.stat().st_size//1024} KB)")

            return True

    except Exception as e:
        print(f"  ERROR: {src.name}: {e}", file=sys.stderr)
        return False


# ---- Main -----------------------------------------------------------
def main():
    src_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_SRC

    if not src_dir.is_dir():
        print(f"ERRORE: cartella origine non trovata: {src_dir}", file=sys.stderr)
        print(f"Creala e mettici dentro le immagini originali, oppure passa un percorso:", file=sys.stderr)
        print(f"  python3 scripts/optimize_images.py /percorso/alle/immagini", file=sys.stderr)
        sys.exit(1)

    # Crea le cartelle di destinazione
    for d in (THUMB_DIR, FULL_DIR, OG_DIR):
        d.mkdir(parents=True, exist_ok=True)

    files = sorted(
        (p for p in src_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXT),
        key=lambda p: p.name,
    )

    if not files:
        print(f"Nessuna immagine trovata in {src_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Elaborazione di {len(files)} immagini da {src_dir}\n")
    ok = 0
    for f in files:
        print(f"- {f.name}")
        if process_image(f):
            ok += 1

    print(f"\nFatto: {ok}/{len(files)} immagini elaborate.")
    print(f"  Thumbnails → {THUMB_DIR.relative_to(PROJECT_ROOT)}")
    print(f"  Full       → {FULL_DIR.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
