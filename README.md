# Pedro Veríssimo — portfolio

Static site, no build step. Vercel serves the repo root; every push to `main` redeploys.

- `index.html` — the whole page (HTML, inline CSS and JS)
- `media/` — photos as WebP in two sizes (`-s` 760px, `-l` 1600px) and silent H.264 loops (`.mp4`) with `-p.webp` posters; metadata (dates, GPS) stripped
- `fonts/` — Geist, Geist Mono, Instrument Serif, Caveat (self-hosted)
- `terminal.txt` + `vercel.json` — `curl -sL pedroverissimo.vercel.app` gets an ANSI text version (routed by user agent)
- `favicon.svg`, `apple-touch-icon.png`, `og.jpg` — icon and link preview

Theme: light / dark / auto (stored in localStorage). The signature intro plays once per browser session and is skipped with reduced motion. Type 1155 on the page.
