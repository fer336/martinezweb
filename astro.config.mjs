import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Dominio temporal propio (Docker/Portainer). Cuando llegue el dominio
// definitivo, solo hay que cambiar "site" acá.
export default defineConfig({
  site: 'https://martinezplomeria.qeva.xyz',
  integrations: [sitemap()],
});
