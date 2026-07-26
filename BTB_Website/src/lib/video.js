// Helpers for turning an interview `video` field into a YouTube id / thumbnail.
// Mirrors the URL parsing in components/VideoEmbed.vue.

const YT_ID = /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{6,})/

export function youtubeId(url) {
  if (!url) return ''
  const m = url.match(YT_ID)
  return m ? m[1] : ''
}

// A shareable preview image for an episode: the YouTube thumbnail when the
// video is on YouTube, otherwise '' (callers fall back to the site cover).
// hqdefault is 4:3 with black letterbox bars — fine for og:image, but for
// on-page cards prefer the 16:9 variants below (no bars, no cropping sliver).
export function videoThumbnail(url) {
  const id = youtubeId(url)
  return id ? `https://img.youtube.com/vi/${id}/hqdefault.jpg` : ''
}

// Crisp 16:9 card thumbnail (1280x720). Not every video has it, so pair it with
// videoThumbnailMq() as an onerror fallback.
export function videoThumbnailHi(url) {
  const id = youtubeId(url)
  return id ? `https://img.youtube.com/vi/${id}/maxresdefault.jpg` : ''
}

// Always-available 16:9 thumbnail (320x180, no black bars) — the safe fallback.
export function videoThumbnailMq(url) {
  const id = youtubeId(url)
  return id ? `https://img.youtube.com/vi/${id}/mqdefault.jpg` : ''
}
