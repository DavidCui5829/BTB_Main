// Small company logos for interviewee orgs. Matched by keyword so minor name
// variations still resolve, and rendered via Google's favicon service — uniform
// treatment for every org with no assets to maintain. Returns '' for an unknown
// org (the UI then shows no logo). Want crisper marks? Drop SVGs in /public and
// return a local path here instead.
const ORG_DOMAINS = [
  [/nasa/i, 'nasa.gov'],
  [/google/i, 'google.com'],
  [/honeywell/i, 'honeywell.com'],
  [/isro/i, 'www.isro.gov.in'],
  [/\bgtt\b/i, 'gtt.fr'], // Gaztransport & Technigaz (gtt.com is a different co.)
  [/phillips\s*66|\bp66\b/i, 'phillips66.com'],
  [/awty/i, 'awty.org'],
]

export function orgDomain(org) {
  if (!org) return ''
  const hit = ORG_DOMAINS.find(([re]) => re.test(org))
  return hit ? hit[1] : ''
}

export function orgLogo(org, size = 64) {
  const domain = orgDomain(org)
  return domain ? `https://www.google.com/s2/favicons?domain=${domain}&sz=${size}` : ''
}
