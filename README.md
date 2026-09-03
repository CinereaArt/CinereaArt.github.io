# Cinerea — Portfolio Agnese Favilla

Sito portfolio statico **Astro** per l'illustratrice e game artist Agnese Favilla (Cinerea).
Deploy automatico su **GitHub Pages** tramite GitHub Actions.

## Struttura del sito

```
/                        → Home (hub: hero + preview delle 3 aree)
/illustration/children   → Children's Illustration
/illustration/editorial  → Editorial Illustration
/game-art                → Game Art & Character Design
/about                   → Bio
/contact                 → Contatti
```

## Comandi principali

```bash
npm install     # installa le dipendenze
npm run dev     # anteprima locale su http://localhost:4321
npm run build   # compila il sito in /dist
npm run preview # serve la build generata
npm run optimize # ottimizza le immagini (vedi sotto)
```

## Come aggiungere un nuovo lavoro (metodo automatico, consigliato)

Non serve scrivere a mano file `.md`. Basta creare una cartella di immagini
nella sezione giusta e rilanciare la build: lo script
`scripts/generate_portfolio.py` genera automaticamente (1) le card nella sezione e
(2) la pagina-progetto con la galleria.

### 1. Crea la cartella del progetto

Le immagini **originali** vivono in `assets/portfolio/<sezione>/<nome-progetto>/`
(cartella gitignorata — NON finiscono nel build). Le sezioni:

| Sezione | Cartella origini | Dove compare |
|---------|------------------|--------------|
| Children's Illustration | `assets/portfolio/children/` | /illustration/children |
| Editorial Illustration  | `assets/portfolio/editorial/` | /illustration/editorial |
| Game Art                | `assets/portfolio/game-art/` | /game-art |

Esempio:

```
assets/portfolio/editorial/editorial-illustration-dune/
├── project.md          (OPZIONALE — vedi sotto)
├── cover.jpg           (OPZIONALE — copertina con precedenza)
├── 01_dune-main.jpg
├── 02_dune-details.jpg
└── 03_dune-final.jpg
```

**Regole di naming:**
- Il nome cartella è lo `slug` del progetto e determina il titolo a build
  (nome normalizzato in Title Case: `editorial-illustration-dune` →
  `Editorial Illustration Dune`).
- Le immagini si mostrano in **ordine alfabetico stabile** per nome file
  (i prefissi numerici `01_`, `02_`, … garantiscono un ordine preciso).
- La **copertina** della card è il primo file in ordine; se esiste un file
  chiamato `cover.<ext>`, quello ha precedenza.
- Formati supportati: jpg, jpeg, png, webp, tiff, bmp.

### 2. Metadati opzionali — `project.md`

Tutti i campi sono **opzionali**; un file anche solo con `title` è valido.
Sovrascrive solo ciò che specifica (il resto ricade sul nome cartella).

```markdown
---
title: "Dune — Editorial Illustration"
year: 2026
role: "Illustrator"
client: "Editor X"
format: "editorial"       # picture-book | editorial | cover | spot | other
featured: true            # compare in homepage
description: >
  Una visione editoriale per il romanzo Dune, tra paesaggi desertici
  e ritratti di personaggi.
tags: ["fantasy", "collage", "editoriale"]
---
```

### 3. Genera e verifica

```bash
npm run optimize        # genera thumb (600px) + full (1600px) in WebP
```

Lo script:
- ottimizza le immagini in `public/images/thumbnails/` e `public/images/portfolio/`
  (WebP, directory per sezione/progetto);
- scrive/riscrive i `.md` in `src/content/portfolio/` (idempotente: a ogni run
  rigenera quelli presenti e pulisce quelli senza origini);
- non tocca i `.md` esistenti (`books-*`, `bn-*`).

Poi:

```bash
npm run build           # controlla che generi card + pagine
git add . && git commit && git push   # GitHub Actions fa build + deploy
```

Il workflow `.github/workflows/deploy.yml` lancia `generate_portfolio.py` prima
di `npm run build`, così il deploy è sempre aggiornato. In CI, dove le origini
gitignorate non sono presenti, lo script esce senza fare nulla e i `.md`/WebP
già versionati bastano al build.

## Aggiungere un lavoro (metodo manuale, solo file .md)


## Tecnica

- **Framework**: Astro 5 (output statico, zero-JS per default)
- **Lightbox**: PhotoSwipe v5
- **Filtri**: JS vanilla (chips client-side)
- **Immagini**: WebP (qualità 82), lazy loading nativo
- **Font**: Inter + Playfair Display
- **Design**: bianco caldo `#FAFAF8` + terracotta `#C4704B`

## Deploy

Il workflow `.github/workflows/deploy.yml` si attiva a ogni push su `main`:
compila con Node 22 e pubblica su GitHub Pages. È gratuito e senza limiti sul repo pubblico.
