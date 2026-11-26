# akandejjohn

Portfolio website for **John Akande** (@akandejjohn), a figurative artist based in Lagos.

A static site with no build step. Pages: `index.html` (home), `works.html` (the catalogue), `about.html` (biography and artist statement), `commission.html` and `contact.html` (enquiries). They share `styles.css`, `script.js` and `assets/`.

The navigation and footer are repeated in each page, so a change to either needs making in all five files.

## Preview locally

```bash
python3 -m http.server 8000
```

Then open http://localhost:8000.

## Deploy

Any static host works (Vercel, Netlify, GitHub Pages, Cloudflare Pages). Point it at the repo root.

## Editing works

Each artwork is a `data-lightbox` button in `works.html` (nine also appear in Selected Works on the home page; phones show the first five). Its `data-title`, `data-meta` and `data-note` attributes set the text shown in the viewer. Images live in `assets/img/` (the catalogue paintings in `assets/img/works/`) and video in `assets/video/`.

## Enquiries

The enquiry form on `contact.html` has no server. It writes the visitor's message, copies it to the clipboard and opens an Instagram direct message to @akandejjohn, where they paste it. A painting's "Enquire about this work" link opens the form with that painting already chosen. To add or remove a painting from the form's list, edit the `<option>` list in `contact.html`.
