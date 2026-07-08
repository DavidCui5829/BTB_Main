import { getByRagId } from '../data/interviews'

// "MichaelAdelemoni" -> "Michael Adelemoni" (mirrors the backend's display logic)
export function displayName(ragId) {
  const person = getByRagId(ragId)
  if (person) return person.name
  return (ragId.match(/[A-Z][a-z]*/g) || [ragId]).join(' ')
}

function escapeHtml(text) {
  return text
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;')
}

// Minimal, safe rendering for assistant replies: escapes HTML, then supports
// **bold**, `code`, and line breaks. Anything fancier stays plain text.
export function renderLite(text) {
  let html = escapeHtml(text)
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')
  html = html.replace(/\n/g, '<br>')
  return html
}
