import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// Deploy actual: GitHub Pages (proyecto "martinezweb").
// Cuando tengan el dominio propio: site: 'https://www.martinezgasplomeria.com.ar', sacar "base".
export default defineConfig({
  site: 'https://fer336.github.io',
  base: '/martinezweb',
  integrations: [sitemap()],
});
