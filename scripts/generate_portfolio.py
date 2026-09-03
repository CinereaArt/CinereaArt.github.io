#!/usr/bin/env python3
"""
Generatore automatico del portfolio per Cinerea.

Il sito permette di aggiungere un progetto al portfolio semplicemente creando
una cartella di immagini in una delle tre sezioni. Questo script, lanciato a
build (o a mano), per ogni progetto:

  1. Ottimizza ogni immagine in WebP (thumb 600px + full 1600px) e le scrive in
       public/images/thumbnails/<sezione>/<slug>/...
       public/images/portfolio/<sezione>/<slug>/...
  2. Legge i metadati opzionali da un file  project.md  (se presente) nella
     cartella del progetto, con fallback sul nome cartella.
  3. Genera (o rigenera, in modo idempotente) il file frontmatter
       src/content/portfolio/<sezione>-<slug>.md
     da cui Astro genera automaticamente card + pagina-progetto con la galleria.

Le immagini ORIGINALI vivono in  assets/portfolio/<sezione>/<slug>/  ed è una
cartella gitignorata: non finiscono MAI nel build. Nel build vanno solo i WebP
ottimizzati (in public/images/) e i .md generati (in src/content/portfolio/),
entrambi versionati.

Se la root delle origini non esiste (es. in CI, dove le origini gitignorate non
sono nel checkout), lo script esce senza fare nulla: NON cancella i .md già
generati e versionati, quindi il build resta valido.

USO:
    python3 scripts/generate_portfolio.py [ROOT_ORIGINI]

ROOT_ORIGINI (opzionale) = cartella che contiene  children/ editorial/ game-art/.
Default: ./assets/portfolio/  dentro il progetto.

DIPENDENZE:
    pip install Pillow   (supporto WebP incluso nelle build standard)

Convenzioni di contesto per la cliente (vedi README):
  - Le sezioni sono cartelle: children / editorial / game-art
  - Ogni progetto è una cartella che prende il nome del progetto (slug).
  - Dentro, le immagini in ordine con prefisso numerico (01_, 02_, ...) o
    qualsiasi ordine alfabetico stabile; il primo file è la copertina, a meno
    che non esista un file chiamato  cover.<ext>  che ha precedenza.
  - Un file  project.md  OPZIONALE può arricchire i metadati (vedi sotto).
"""

import re
import sys
from pathlib import Path

from PIL import Image

# ---------------------------------------------------------------------------
# Configurazione
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_ROOT = PROJECT_ROOT / "assets" / "portfolio"

THUMB_DIR = PROJECT_ROOT / "public" / "images" / "thumbnails"
FULL_DIR = PROJECT_ROOT / "public" / "images" / "portfolio"
PORTFOLIO_DIR = PROJECT_ROOT / "src" / "content" / "portfolio"

# Sezioni ammesse: nome cartella origini -> categoria/subcategoria Astro
SECTIONS = {
    "children": {"category": "illustration", "subcategory": "children"},
    "editorial": {"category": "illustration", "subcategory": "editorial"},
    "game-art": {"category": "character-design", "subcategory": None},
}

# Raster supportati
ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".tiff", ".bmp"}

# Dimensioni max (lato lungo) e qualità WebP (coerenti con optimize_images.py)
THUMB_MAX = 600
FULL_MAX = 1600
WEBP_QUALITY = 82

# Etichetta di cui i .md generati sono riconoscibili dentro portfolio/
# (per pulizia idempotente). Si lega al prefisso del nome file.
GEN_PREFIXES = ("children-", "editorial-", "game-art-")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def natural_key(name: str) -> list:
    """Chiave di ordinamento 'naturale': '01_' < '02_' < ... < '10_' < '11_'.
    Tratta i numeri come valori numerici, non come stringhe."""
    base = Path(name).stem
    return [int(part) if part.isdigit() else part.lower() for part in re.split(r"(\d+)", base)]


def title_case(folder_name: str) -> str:
    """'editorial-illustration_dune' -> 'Editorial Illustration Dune'."""
    words = [w for w in re.split(r"[\s_+\-]+", folder_name) if w]
    return " ".join(w.capitalize() for w in words)


def slugify(name: str) -> str:
    """Normalizza un nome in slug URL-safe (minuscolo, separatori -> '-')."""
    base = re.sub(r"[\s_+]+", "-", name).strip("-")
    base = re.sub(r"[^a-z0-9\-]+", "-", base.lower()).strip("-")
    return base or "progetto"


def optimize_image(src: Path, thumb_path: Path, full_path: Path) -> bool:
    """Ottimizza una singola immagine -> thumb + full WebP. True se riuscita."""
    try:
        with Image.open(src) as im:
            if im.mode in ("RGBA", "LA"):
                im = im.convert("RGBA")
            else:
                im = im.convert("RGB")

            full = im.copy()
            full.thumbnail((FULL_MAX, FULL_MAX), Image.LANCZOS)
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full.save(full_path, "WEBP", quality=WEBP_QUALITY, method=6)

            thumb = im.copy()
            thumb.thumbnail((THUMB_MAX, THUMB_MAX), Image.LANCZOS)
            thumb_path.parent.mkdir(parents=True, exist_ok=True)
            thumb.save(thumb_path, "WEBP", quality=WEBP_QUALITY, method=6)
            return True
    except Exception as e:  # noqa: BLE001
        print(f"      [ERRORE immagine] {src.name}: {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------------------
# Parsing di project.md (mini-parser YAML-friendly, tollerante)
# ---------------------------------------------------------------------------
def parse_project_md(path: Path) -> dict:
    """Legge project.md e ritorna un dict con i campi conosciuti.
    Accetta sia frontmatter '---' sia file semplice 'chiave: valore'.
    Gli errori non bloccano: si usa il fallback sul nome cartella."""
    fields = {}
    if not path.is_file():
        return fields

    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception as e:  # noqa: BLE001
        print(f"      [avviso] project.md illeggibile ({e}); uso fallback")
        return fields

    # Rimuove i delimitatori di frontmatter (---) se presenti
    lines = [ln for ln in lines if ln.strip() != "---"]

    current_key = None
    for raw in lines:
        stripped = raw.rstrip()
        if not stripped.strip():
            continue
        # Linea indentata -> continuazione (multi-line value)
        if current_key and (raw.startswith("  ") or raw.startswith("\t")):
            fields[current_key] = (fields.get(current_key, "") + "\n" + stripped.strip()).strip()
            continue
        m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*:\s*(.*)$", stripped)
        if m:
            current_key = m.group(1).lower()
            value = m.group(2).strip()
            # Rimuove eventuali virgolette esterne (YAML 'abc' / "abc")
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            fields[current_key] = value
        else:
            current_key = None
    return fields


def coerce_field(fields: dict, name: str, parser, default=None):
    """Applica un parser a un campo, con fallback."""
    if name in fields and fields[name] not in ("", None):
        try:
            return parser(fields[name])
        except Exception:  # noqa: BLE001
            return default
    return default


def parse_int(value: str):
    return int(str(value).strip())


def parse_bool(value: str):
    v = str(value).strip().lower()
    return v in ("true", "1", "yes", "si", "sì")


def parse_tags(value):
    v = str(value).strip()
    if v.startswith("["):
        v = v.strip("[]")
    return [t.strip().strip("\"'") for t in v.split(",") if t.strip()]


# ---------------------------------------------------------------------------
# Scrittura .md
# ---------------------------------------------------------------------------
def write_md(meta: dict, filename: str) -> None:
    """Scrive il .md per un progetto in src/content/portfolio/<filename>."""
    def q(s):
        return '"' + str(s).replace('"', '\\"') + '"'

    frontmatter = []
    frontmatter.append(f"title: {q(meta['title'])}")
    frontmatter.append(f"category: {q(meta['category'])}")
    if meta.get("subcategory"):
        frontmatter.append(f"subcategory: {q(meta['subcategory'])}")
    if meta.get("format"):
        frontmatter.append(f"format: {q(meta['format'])}")
    if meta.get("date"):
        frontmatter.append(f"date: {meta['date']}")
    if meta.get("description"):
        # multiline description
        desc_lines = str(meta["description"]).splitlines()
        frontmatter.append("description: |")
        for line in desc_lines:
            frontmatter.append(f"  {line}")
    if meta.get("tags"):
        tag_str = ", ".join(f'"{t}"' for t in meta["tags"])
        frontmatter.append(f"tags: [{tag_str}]")
    if meta.get("client"):
        frontmatter.append(f"client: {q(meta['client'])}")
    if meta.get("year"):
        frontmatter.append(f"year: {meta['year']}")
    if meta.get("role"):
        frontmatter.append(f"role: {q(meta['role'])}")
    if meta.get("featured"):
        frontmatter.append(f"featured: {str(meta['featured']).lower()}")
    if meta.get("group"):
        frontmatter.append(f"group: {q(meta['group'])}")

    frontmatter.append(f"image: {q(meta['image'])}")
    frontmatter.append(f"imageFull: {q(meta['imageFull'])}")

    if meta.get("gallery"):
        frontmatter.append("gallery:")
        for item in meta["gallery"]:
            frontmatter.append(f"  - src: {q(item['src'])}")
            frontmatter.append(f"    alt: {q(item['alt'])}")

    content = "---\n" + "\n".join(frontmatter) + "\n---\n"
    PORTFOLIO_DIR.mkdir(parents=True, exist_ok=True)
    (PORTFOLIO_DIR / filename).write_text(content, encoding="utf-8")
    print(f"    [md] {filename}")


# ---------------------------------------------------------------------------
# Processo di una singola cartella progetto
# ---------------------------------------------------------------------------
def process_project(section: str, project_dir: Path):
    section_meta = SECTIONS[section]
    slug = slugify(project_dir.name)
    if not slug:
        return False

    # Raccolta file immagine (esclusi project.md) e metadati
    images = sorted(
        (p for p in project_dir.iterdir() if p.is_file() and p.suffix.lower() in ALLOWED_EXT),
        key=lambda p: natural_key(p.name),
    )
    if not images:
        print(f"      [salto] {project_dir.name}: nessuna immagine")
        return False

    # Cover: il primo file in ordine, a meno che non esista cover.<ext>
    cover_file = next((p for p in images if Path(p.stem).name.lower() == "cover"), None)
    if cover_file is not None:
        images = [cover_file] + [p for p in images if p is not cover_file]

    # Metadati: project.md opzionale
    meta = parse_project_md(project_dir / "project.md")
    title = str(meta.get("title") or "").strip() or title_case(project_dir.name)

    # Percorsi WebP
    thumb_dir = THUMB_DIR / section / slug
    full_dir = FULL_DIR / section / slug

    # Ottimizza immagini e builda la gallery
    gallery = []
    n = 0
    for img in images:
        stem = slugify(img.stem)
        thumb_path = thumb_dir / f"{stem}.webp"
        full_path = full_dir / f"{stem}.webp"
        if not optimize_image(img, thumb_path, full_path):
            continue
        n += 1
        full_rel = f"/images/portfolio/{section}/{slug}/{stem}.webp"
        thumb_rel = f"/images/thumbnails/{section}/{slug}/{stem}.webp"
        # Miglior alt quando possibile altrimenti '<Titolo> — immagine N'
        better = str(meta.get("description") or "").strip()
        alt = f"{title} — immagine {n}" if not better else f"{title} — {better[:80]}"
        gallery.append({"src": full_rel, "thumb": thumb_rel, "alt": alt})

    if not gallery:
        print(f"      [salto] {project_dir.name}: nessuna immagine elaborata")
        return False

    cover = gallery[0]

    # Data: da project.md (YYYY-MM-DD / YYYY-MM-DD) o oggi
    date = coerce_field(meta, "date", str, None)
    if date and not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        date = None

    write_md(
        {
            "title": title,
            "category": section_meta["category"],
            "subcategory": section_meta["subcategory"],
            "format": coerce_field(meta, "format", str, None).strip() if coerce_field(meta, "format", str, None) else None,
            "date": date,
            "description": coerce_field(meta, "description", str, None),
            "tags": coerce_field(meta, "tags", parse_tags, []),
            "client": coerce_field(meta, "client", str, None),
            "year": coerce_field(meta, "year", parse_int, None),
            "role": coerce_field(meta, "role", str, None),
            "featured": coerce_field(meta, "featured", parse_bool, False),
            "group": f"generated-{section}",
            "image": cover["thumb"],
            "imageFull": cover["src"],
            "gallery": [{"src": g["src"], "alt": g["alt"]} for g in gallery],
        },
        f"{section}-{slug}.md",
    )
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_ROOT

    # In CI le origini gitignorate non ci sono: non fare nulla, NON cancellare
    # i .md già generati e versionati (altrimenti il build resterebbe vuoto).
    if not root.is_dir():
        print(f"[generate_portfolio] root origini non trovata ({root}).")
        print("[generate_portfolio] Nessuna generazione: i .md esistenti restano intatti.")
        return

    print(f"[generate_portfolio] Elaboro origini da {root}")
    generated_filenames = set()

    for section, meta in SECTIONS.items():
        section_dir = root / section
        if not section_dir.is_dir():
            continue
        print(f"  Sezione: {section}")
        for project_dir in sorted(
            (p for p in section_dir.iterdir() if p.is_dir() and not p.name.startswith(".")),
            key=lambda p: p.name.lower(),
        ):
            print(f"    Progetto: {project_dir.name}")
            before = sorted(generated_filenames)
            if process_project(section, project_dir):
                generated_filenames.add(f"{section}-{slugify(project_dir.name)}.md")
            else:
                generated_filenames.difference_update(before)

    # Pulizia idempotente: rimuove i .md generati in un run precedente di cui
    # NON esistono più le origini (solo se la root esiste, ovvero siamo locali).
    if PORTFOLIO_DIR.is_dir():
        for f in sorted(PORTFOLIO_DIR.iterdir()):
            if f.is_file() and f.suffix == ".md" and f.name.startswith(GEN_PREFIXES):
                if f.name not in generated_filenames:
                    f.unlink()
                    print(f"    [pulito] {f.name} (origini rimosse)")

    print(f"[generate_portfolio] Fatto: {len(generated_filenames)} progetti generati.")


if __name__ == "__main__":
    main()
