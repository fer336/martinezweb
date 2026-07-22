import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Cambiá site por tu dominio real antes de publicar.
export default defineConfig({
  site: 'https://www.martinezgasplomeria.com.ar',
  integrations: [sitemap()],
});
