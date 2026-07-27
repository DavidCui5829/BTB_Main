// Single source of truth for page SEO (title / description / canonical /
// Open Graph / Twitter / JSON-LD). Pure and framework-free so it can run in
// BOTH places that need it:
//   - the client composable useSeo() (updates the live <head> on navigation)
//   - the build-time prerender plugin (bakes the same tags into static HTML)
// Keeping them in lockstep is the whole point — crawlers and users see the same.

import { videoThumbnail, youtubeId } from './video'

export const SITE = {
  url: 'https://thebtbpodcast.com',
  name: 'Beyond the Blueprint',
  defaultImage: 'https://thebtbpodcast.com/btb-cover.png',
}

export const HOME_DESCRIPTION =
  'Created by students, for students. Real video interviews with engineers at ' +
  'NASA, Google and ISRO, plus a personalized AI that answers your ' +
  'engineering-career questions from every conversation.'

// Trim to a clean, meta-description-friendly length on a word boundary.
export function clamp(text, max = 160) {
  if (!text) return ''
  const t = text.replace(/\s+/g, ' ').trim()
  if (t.length <= max) return t
  const cut = t.slice(0, max - 1)
  return cut.slice(0, cut.lastIndexOf(' ')).trim() + '…'
}

// SEO descriptor for the homepage.
export function homeSeo(interviews) {
  return {
    title: 'Beyond the Blueprint: What Engineers Actually Do',
    description: HOME_DESCRIPTION,
    path: '/',
    type: 'website',
    image: SITE.defaultImage,
    imageWidth: 1024,
    imageHeight: 1024,
    jsonLd: {
      '@context': 'https://schema.org',
      '@type': 'ItemList',
      name: 'Beyond the Blueprint interviews',
      itemListElement: interviews.map((p, i) => ({
        '@type': 'ListItem',
        position: p.episode ?? i + 1,
        url: `${SITE.url}/interviews/${p.id}`,
        name: `${p.name} · ${p.role}, ${p.org}`,
      })),
    },
  }
}

// SEO descriptor for a single interview/episode page.
export function interviewSeo(p) {
  const url = `${SITE.url}/interviews/${p.id}`
  const ytThumb = videoThumbnail(p.video)
  const image = ytThumb || SITE.defaultImage
  const ytId = youtubeId(p.video)

  return {
    title: `${p.name} · ${p.role}, ${p.org} | Beyond the Blueprint`,
    description: clamp(`${p.role} at ${p.org}. ${p.intro}`),
    path: `/interviews/${p.id}`,
    image,
    imageWidth: ytThumb ? 480 : 1024,
    imageHeight: ytThumb ? 360 : 1024,
    type: 'article',
    jsonLd: {
      '@context': 'https://schema.org',
      '@graph': [
        {
          '@type': 'PodcastEpisode',
          url,
          name: `${p.name}: ${p.role} at ${p.org}`,
          episodeNumber: p.episode,
          ...(p.date && { datePublished: p.date }),
          description: clamp(p.intro, 300),
          image,
          partOfSeries: {
            '@type': 'PodcastSeries',
            name: SITE.name,
            url: `${SITE.url}/`,
          },
          about: {
            '@type': 'Person',
            name: p.name,
            jobTitle: p.role,
            worksFor: { '@type': 'Organization', name: p.org },
          },
          ...(p.video && {
            video: {
              '@type': 'VideoObject',
              name: `Beyond the Blueprint: ${p.name}`,
              description: clamp(p.intro, 300),
              thumbnailUrl: image,
              ...(p.date && { uploadDate: p.date }),
              ...(ytId
                ? { embedUrl: `https://www.youtube.com/embed/${ytId}` }
                : { contentUrl: `${SITE.url}${p.video}` }),
            },
          }),
        },
        {
          '@type': 'BreadcrumbList',
          itemListElement: [
            { '@type': 'ListItem', position: 1, name: 'Home', item: `${SITE.url}/` },
            { '@type': 'ListItem', position: 2, name: 'Interviews', item: `${SITE.url}/#interviews` },
            { '@type': 'ListItem', position: 3, name: p.name, item: url },
          ],
        },
      ],
    },
  }
}

// ---- build-time rendering (used by the prerender plugin) --------------------

function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
}

// Render an SEO descriptor to the exact <head> tags useSeo() sets at runtime.
// Returned as an HTML string for injection between the index.html markers.
export function renderHeadTags(seo) {
  const url = SITE.url + (seo.path || '/')
  const image = seo.image || SITE.defaultImage
  const type = seo.type || 'website'
  const title = seo.title || SITE.name
  const desc = seo.description || ''

  const tags = [
    `<meta name="description" content="${esc(desc)}" />`,
    `<title>${esc(title)}</title>`,
    `<link rel="canonical" href="${esc(url)}" />`,
    `<meta property="og:site_name" content="${esc(SITE.name)}" />`,
    `<meta property="og:type" content="${esc(type)}" />`,
    `<meta property="og:title" content="${esc(title)}" />`,
    `<meta property="og:description" content="${esc(desc)}" />`,
    `<meta property="og:url" content="${esc(url)}" />`,
    `<meta property="og:image" content="${esc(image)}" />`,
    ...(seo.imageWidth
      ? [
          `<meta property="og:image:width" content="${esc(seo.imageWidth)}" />`,
          `<meta property="og:image:height" content="${esc(seo.imageHeight)}" />`,
        ]
      : []),
    `<meta name="twitter:card" content="summary_large_image" />`,
    `<meta name="twitter:title" content="${esc(title)}" />`,
    `<meta name="twitter:description" content="${esc(desc)}" />`,
    `<meta name="twitter:image" content="${esc(image)}" />`,
  ]

  if (seo.jsonLd) {
    const json = JSON.stringify(seo.jsonLd).replace(/</g, '\\u003c')
    tags.push(`<script type="application/ld+json" id="route-jsonld">${json}</script>`)
  }

  return tags.join('\n    ')
}

// Render a crawlable static <body> for an interview page: heading, intro,
// highlights and the full transcript. The prerender plugin injects this into the
// #app element so non-JS crawlers (Bing, GPTBot, social unfurlers) and first
// paint get the real content; Vue replaces #app with the interactive page when
// it mounts, so users still get the full experience.
export function renderInterviewBody(p, paragraphs = []) {
  const out = [
    `<main class="detail"><div class="container">`,
    `<p class="meta">EP ${String(p.episode).padStart(2, '0')} · ${esc(p.field)}</p>`,
    `<h1>${esc(p.name)}</h1>`,
    `<p class="byline">${esc(p.role)} · ${esc(p.org)}</p>`,
  ]
  if (p.intro) out.push(`<section class="bio"><h2>About</h2><p>${esc(p.intro)}</p></section>`)
  if (p.highlights && p.highlights.length) {
    out.push(
      `<section class="highlights"><h2>In this episode</h2><ul>` +
        p.highlights.map((h) => `<li>${esc(h)}</li>`).join('') +
        `</ul></section>`
    )
  }
  if (p.quote) {
    out.push(`<blockquote class="quote"><p>${esc(p.quote)}</p><cite>${esc(p.name)}</cite></blockquote>`)
  }
  if (paragraphs.length) {
    out.push(
      `<section class="transcript"><h2>Full transcript</h2>` +
        paragraphs.map((t) => `<p>${esc(t)}</p>`).join('') +
        `</section>`
    )
  }
  out.push(`</div></main>`)
  return out.join('\n')
}

// Crawlable static <body> for the homepage: heading, tagline and links to every
// episode (helps crawlers discover the interview pages from raw HTML).
export function renderHomeBody(interviews) {
  const items = interviews
    .map(
      (p) =>
        `<li><a href="/interviews/${p.id}">${esc(p.name)} · ${esc(p.role)}, ${esc(p.org)}</a></li>`
    )
    .join('')
  return [
    `<main><div class="container">`,
    `<h1>${esc(SITE.name)}: What Engineers Actually Do</h1>`,
    `<p>${esc(HOME_DESCRIPTION)}</p>`,
    `<h2>Interviews</h2>`,
    `<ul>${items}</ul>`,
    `</div></main>`,
  ].join('\n')
}
