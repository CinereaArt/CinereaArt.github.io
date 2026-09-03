import { defineCollection, z } from 'astro:content';

const portfolio = defineCollection({
  type: 'content',
  schema: () =>
    z.object({
      // Titolo dell'opera/progetto
      title: z.string(),

      // Macro-area: illustration | character-design
      // Questa è la distinzione principale (illustratrice vs game artist)
      category: z.enum(['illustration', 'character-design']),

      // Sotto-categoria OBBLIGATORIA per l'illustrazione: children | editorial
      // Per character-design si omette (il nome della cartella lo definisce)
      subcategory: z.enum(['children', 'editorial']).optional(),

      // Formato di pubblicazione / tipo (es. picture book, cover, book spread)
      format: z.enum(['picture-book', 'editorial', 'cover', 'spot', 'other']).optional(),

      // Data di creazione (per ordinamento)
      date: z.coerce.date().optional(),

      // Descrizione dell'opera (per SEO + alt text)
      description: z.string().optional(),

      // Tags liberi per filtraggio (es. "fox", "forest", "acquerello digitale")
      tags: z.array(z.string()).default([]),

      // Gruppo di provenienza (books / bn) — informativo, per futuri filtraggi
      group: z.string().optional(),

      // Metadati professionali (client, anno, ruolo) — si mostrano nella project page
      client: z.string().optional(),
      year: z.coerce.number().optional(),
      role: z.string().optional(),

      // Immagine principale (thumbnail per la griglia)
      // Path relativo a /public (es. "/images/thumbnails/portfolio0.webp")
      image: z.string().optional(),

      // Immagine full per il lightbox (path relativo a /public)
      imageFull: z.string().optional(),

      // Se featured → compare nella homepage
      featured: z.boolean().default(false),

      // Ordinamento manuale
      order: z.number().optional(),
    }),
});

const publications = defineCollection({
  type: 'content',
  schema: () =>
    z.object({
      // Titolo del libro / pubblicazione
      title: z.string(),

      // Tipo di pubblicazione
      type: z.enum(['picture-book', 'book', 'anthology', 'magazine', 'other']).default('book'),

      // Casa editrice
      publisher: z.string(),

      // Anno di pubblicazione (per ordinamento)
      year: z.coerce.number().optional(),

      // Ruolo (autrice/illustratrice/cover)
      role: z.string().optional(),

      // Link esterno (optional)
      link: z.string().optional(),
    }),
});

const publishers = defineCollection({
  type: 'content',
  schema: () =>
    z.object({
      // Nome della casa editrice / studio
      name: z.string(),

      // Tipo (editrice, studio, rivista)
      kind: z.enum(['publisher', 'studio', 'magazine', 'other']).default('publisher'),

      // Sito web
      url: z.string().optional(),

      // Breve nota (opzionale)
      note: z.string().optional(),

      // Ordinamento
      order: z.number().optional(),
    }),
});

export const collections = { portfolio, publications, publishers };
