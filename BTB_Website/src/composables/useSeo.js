// Client-side head management for the SPA. On every route it updates the same
// tags the build-time prerender bakes into the static HTML (see src/lib/seo.js),
// so what Google renders and what a user navigates to always match.

import { watchEffect } from 'vue'
import { SITE } from '../lib/seo'

export { SITE } from '../lib/seo'

function upsertMeta(attr, key, content) {
  if (!content) return
  let el = document.head.querySelector(`meta[${attr}="${key}"]`)
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attr, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function upsertLink(rel, href) {
  if (!href) return
  let el = document.head.querySelector(`link[rel="${rel}"]`)
  if (!el) {
    el = document.createElement('link')
    el.setAttribute('rel', rel)
    document.head.appendChild(el)
  }
  el.setAttribute('href', href)
}

function setJsonLd(data) {
  const id = 'route-jsonld'
  const existing = document.getElementById(id)
  if (!data) {
    if (existing) existing.remove()
    return
  }
  const el = existing || document.createElement('script')
  el.type = 'application/ld+json'
  el.id = id
  el.textContent = JSON.stringify(data)
  if (!existing) document.head.appendChild(el)
}

// Accepts a plain SEO descriptor or a getter returning one (so reactive route
// data updates the head). Fields: title, description, path, image, type, jsonLd.
export function useSeo(source) {
  watchEffect(() => {
    const s = typeof source === 'function' ? source() : source
    if (!s) return

    const title = s.title || SITE.name
    const description = s.description || ''
    const url = SITE.url + (s.path || '/')
    const image = s.image || SITE.defaultImage
    const type = s.type || 'website'

    document.title = title
    upsertMeta('name', 'description', description)
    upsertLink('canonical', url)

    upsertMeta('property', 'og:site_name', SITE.name)
    upsertMeta('property', 'og:type', type)
    upsertMeta('property', 'og:title', title)
    upsertMeta('property', 'og:description', description)
    upsertMeta('property', 'og:url', url)
    upsertMeta('property', 'og:image', image)
    if (s.imageWidth) {
      upsertMeta('property', 'og:image:width', String(s.imageWidth))
      upsertMeta('property', 'og:image:height', String(s.imageHeight))
    }

    upsertMeta('name', 'twitter:card', 'summary_large_image')
    upsertMeta('name', 'twitter:title', title)
    upsertMeta('name', 'twitter:description', description)
    upsertMeta('name', 'twitter:image', image)

    setJsonLd(s.jsonLd || null)
  })
}
