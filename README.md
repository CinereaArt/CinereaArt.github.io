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

## Come aggiungere un nuovo lavoro

### 1. Ottimizza le immagini
Metti le immagini originali in `assets/originals/`, poi:
```bash
npm run optimize
```
Genera automaticamente thumbnail (600px) e full (1600px) in WebP.

### 2. Crea il frontmatter
Crea un file `.md` in `src/content/portfolio/` (es. `il-mio-lavoro.md`):

```markdown
---
title: "Titolo dell'opera"
category: "illustration"        # oppure: "character-design"
subcategory: "children"         # solo per illustration: "children" | "editorial"
format: "picture-book"          # optional: picture-book | cover | editorial | spot
date: 2026-09-01
description: "Breve descrizione dell'opera."
tags: ["fantasy", "acquerello"]
client: "Editor X"              # optional
year: 2026                      # optional
featured: true                  # optional: appare in homepage
---

Testo libero descrittivo (opzionale).
```

**Valori categoria:**
- `category: "illustration"` → compare nelle pagine Illustration (children/editorial)
- `category: "character-design"` → compare nella pagina Game Art

### 3. Commit e push
```bash
git add .
git commit -m "Aggiunto lavoro: <titolo>"
git push
```
GitHub Actions compila e pubblica automaticamente.

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
