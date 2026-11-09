# Pedro Veríssimo — portfolio

Static site, no build step. Vercel serves the repo root; every push to `main` redeploys.

- `index.html` — the whole page (HTML, inline CSS and JS)
- `media/` — photos as WebP in two sizes (`-s` 760px, `-l` 1600px), metadata stripped
- `fonts/` — Geist and Geist Mono (self-hosted)
- `favicon.svg`, `apple-touch-icon.png`, `og.jpg` — icon and link preview

Theme: light / dark / auto, toggle in the header (stored in localStorage).
The signature intro plays once per browser session and is skipped with reduced motion.
