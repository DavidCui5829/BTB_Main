import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import path from 'node:path'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import {
  SITE,
  homeSeo,
  interviewSeo,
  renderHeadTags,
  renderInterviewBody,
  renderHomeBody,
} from './src/lib/seo.js'

const SEO_MARKER = /<!--seo-start-->[\s\S]*?<!--seo-end-->/
const APP_DIV = '<div id="app"></div>'

function readInterviews(root) {
  return JSON.parse(
    readFileSync(path.resolve(root, 'src/data/interviews.json'), 'utf-8')
  )
}

function readTranscript(root, id) {
  try {
    const raw = readFileSync(
      path.resolve(root, 'src/data/transcripts', `${id}.json`),
      'utf-8'
    )
    return JSON.parse(raw).paragraphs || []
  } catch {
    return []
  }
}

// Build-time SEO: emit a sitemap and prerender one static HTML file per route
// with that page's real <head>. No headless browser — plain Node, so the
// server-side `npm run build` (admin rebuilds) works unchanged. Users still get
// the normal SPA once the JS boots; crawlers/social get correct tags immediately.
function seoBuild() {
  let root = process.cwd()
  let outDir = 'dist'

  return {
    name: 'btb-seo-build',
    apply: 'build',
    configResolved(c) {
      root = c.root
      outDir = c.build.outDir
    },

    generateBundle() {
      const interviews = readInterviews(root)
      const lastmod = new Date().toISOString().slice(0, 10)
      const urls = [
        { loc: `${SITE.url}/`, priority: '1.0', changefreq: 'weekly' },
        ...interviews.map((p) => ({
          loc: `${SITE.url}/interviews/${p.id}`,
          priority: '0.8',
          changefreq: 'monthly',
        })),
      ]
      const body = urls
        .map(
          (u) =>
            `  <url>\n` +
            `    <loc>${u.loc}</loc>\n` +
            `    <lastmod>${lastmod}</lastmod>\n` +
            `    <changefreq>${u.changefreq}</changefreq>\n` +
            `    <priority>${u.priority}</priority>\n` +
            `  </url>`
        )
        .join('\n')
      const xml =
        `<?xml version="1.0" encoding="UTF-8"?>\n` +
        `<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n` +
        `${body}\n</urlset>\n`
      this.emitFile({ type: 'asset', fileName: 'sitemap.xml', source: xml })
    },

    closeBundle() {
      const distDir = path.resolve(root, outDir)
      const template = readFileSync(path.join(distDir, 'index.html'), 'utf-8')

      if (!SEO_MARKER.test(template)) {
        console.warn('[btb-seo-build] SEO markers missing in index.html — prerender skipped')
        return
      }

      // Bake the per-page <head>, and (when given) real body content into the
      // #app element so crawlers/first-paint see it. Vue replaces #app on mount,
      // so users still get the full interactive SPA.
      const inject = (seo, body) => {
        let html = template.replace(
          SEO_MARKER,
          `<!--seo-start-->\n    ${renderHeadTags(seo)}\n    <!--seo-end-->`
        )
        if (body) html = html.replace(APP_DIV, `<div id="app">${body}</div>`)
        return html
      }

      const interviews = readInterviews(root)

      // Homepage: generated <head> + a crawlable body (intro + episode links).
      writeFileSync(
        path.join(distDir, 'index.html'),
        inject(homeSeo(interviews), renderHomeBody(interviews))
      )

      // One flat static file per episode (interviews/<id>.html), served by
      // nginx via `try_files $uri $uri.html ...` — no trailing-slash redirect,
      // so the served URL matches the no-slash canonical exactly. The full
      // transcript is baked into the body for indexing.
      const interviewsDir = path.join(distDir, 'interviews')
      mkdirSync(interviewsDir, { recursive: true })
      for (const p of interviews) {
        const body = renderInterviewBody(p, readTranscript(root, p.id))
        writeFileSync(path.join(interviewsDir, `${p.id}.html`), inject(interviewSeo(p), body))
      }

      console.log(`[btb-seo-build] prerendered home + ${interviews.length} interview pages`)
    },
  }
}

export default defineConfig({
  plugins: [vue(), seoBuild()],
  server: {
    port: 5173,
    open: false,
  },
})
