// @ts-check
import { defineConfig } from 'astro/config';

// https://astro.build/config
export default defineConfig({
  site: 'https://CinereaArt.github.io',
  // GitHub Pages serve il sito dalla root di user.github.io, quindi base è '/'
  // Se in futuro si passa a un custom domain o a un path type (project pages),
  // aggiornare 'base' di conseguenza.
  base: '/',
});
