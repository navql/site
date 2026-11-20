# NavQL website

Static site for [NavQL](https://navql.com/), a free database client for macOS, Windows and Linux.

Plain HTML/CSS, no build step. Served by GitHub Pages from the `main` branch root.

- `index.html`: home page (its own inline CSS).
- `<database>-client/` and `alternatives/`: one page per database and per comparison, sharing `assets/pages.css`. They are
  written by `tools/pages.py` (content lives in that script), which also writes the footer of `index.html` and `sitemap.xml`.
  After changing it, run `python3 tools/pages.py` and commit the generated HTML.
- `llms.txt`: product facts for AI search engines. Keep it in step with the app's README.

Run locally:

```bash
python3 -m http.server 8770
```
