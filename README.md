# Martínez Gas-Plomería — Sitio Astro

Sitio estático multipágina con SEO local + GEO. Service oficial Rowa y Grundfos · Pinamar y la Costa.

## Correr

```bash
npm install
npm run dev        # http://localhost:4321
npm run build      # genera /dist estático
npm run preview
```

## Antes de publicar
1. `astro.config.mjs` → poné tu dominio real en `site`.
2. `src/data/site.json` → confirmá teléfono, WhatsApp, PLACE_ID de Google, redes.
3. `public/assets/` → reemplazá/añadí fotos reales de trabajos.
4. Enviá `sitemap-index.xml` a Google Search Console.

## Estructura
- `src/layouts/BaseLayout.astro` — head, metadatos, JSON-LD LocalBusiness, header, footer, botón WhatsApp flotante.
- `src/components/` — bloques reutilizables (Hero, secciones, FAQ con JSON-LD, etc).
- `src/pages/` — una página real por URL (home, servicios, zonas, blog, contacto).
- `src/data/` — contenido en JSON (zonas, servicios, reseñas, faqs, datos del negocio).
- `src/styles/global.css` — paleta blanco/negro/amarillo #F6C500, tipografías.

## SEO / GEO
- Metadatos + canonical + Open Graph por página (props del layout).
- JSON-LD: `Plumber` (home), `FAQPage` (home y servicios), `Article` (blog).
- Sitemap automático (@astrojs/sitemap) + robots.txt.
- Una página por zona; NAP consistente desde `site.json`.
