# akandejjohn

Portfolio website for **John Akande** (@akandejjohn), a figurative artist based in Lagos.

A static site with no build step: `index.html`, `styles.css`, `script.js` and `assets/`.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy

Any static host works (Vercel, Netlify, GitHub Pages, Cloudflare Pages). Point it at the repo root.

## Editing works

Each artwork is a `data-lightbox` button in `index.html`. Its `data-title`, `data-meta` and `data-note` attributes set the text shown in the viewer. Images live in `assets/img/` and video in `assets/video/`.
