# BTB deployment

The site is live at **https://thebtbpodcast.com** on a CentOS Stream 9 box.

| Piece      | Where on the server                                     |
| ---------- | ------------------------------------------------------- |
| Front end  | `/opt/btb/BTB_Website/dist` (built there, served by nginx) |
| Backend    | `/opt/btb/BTB_AI`, systemd unit `btb-backend` (uvicorn on `127.0.0.1:8000`) |
| nginx      | `/etc/nginx/conf.d/btb.conf` — serves the SPA, proxies `/api/` → backend |
| TLS        | Let's Encrypt (`certbot`), auto-renewed                 |
| Backend env| `/opt/btb/BTB_AI/.env` (API keys, `DEEPSEEK_MODEL`, admin token) |

Access is via SSH key `~/.ssh/btb_deploy` (already authorized as `root`), so the
scripts need no password. Override the target with `BTB_HOST` / `BTB_SSH_KEY`.

## Deploy after a local change

```bash
# Front-end changes (Vue, index.html, SEO, styles, interviews.js …)
bash deploy/deploy_frontend.sh

# Backend changes (BTB_AI app code)
bash deploy/deploy_backend.sh
```

**deploy_frontend.sh** builds locally as a check, syncs the source, then rebuilds
on the server (so edits made through the `/admin` page — which live only in the
server's `src/data/interviews.json` — are preserved). A failed server build rolls
back to the previous `dist`.

**deploy_backend.sh** syncs the app code and restarts `btb-backend`, preserving
the server's `.env` and its built `vectorstore`, then waits for `/health`.

## How the SEO / prerendering works

`npm run build` runs a small plugin ([BTB_Website/vite.config.js](../BTB_Website/vite.config.js))
that, with **no headless browser**, writes one static file per route:

- `dist/index.html` — homepage `<head>`
- `dist/interviews/<id>.html` — one per episode, each with its own title,
  description, canonical, Open Graph / Twitter tags (YouTube thumbnail as the
  share image) and `PodcastEpisode` JSON-LD.
- `dist/sitemap.xml`, `dist/robots.txt`

All of it is generated from one source of truth,
[BTB_Website/src/lib/seo.js](../BTB_Website/src/lib/seo.js), which the client
composable `useSeo()` also uses — so the static HTML and the live SPA always match.
Real users still get the normal Vue app once JS boots; crawlers and social
scrapers get correct tags immediately.

nginx serves these via `try_files $uri $uri.html $uri/ /index.html;` (the
`$uri.html` part is what serves `interviews/<id>.html` for a clean, no-redirect
URL — keep it if you ever edit the nginx config).

## SEO — one-time tasks (need your Google account)

1. **Google Search Console** → add property `thebtbpodcast.com`, verify (DNS TXT
   or the HTML-tag method), then **Sitemaps → submit** `sitemap.xml`.
2. **Bing Webmaster Tools** → same, or just import from Search Console.
3. Request indexing for the homepage and a couple of episode URLs to speed things up.

The sitemap (`/sitemap.xml`) and `robots.txt` are generated/served automatically;
the sitemap regenerates from the interview catalog on every build.
