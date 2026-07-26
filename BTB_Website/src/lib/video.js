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
export function videoThumbnail(url) {
  const id = youtubeId(url)
  return id ? `https://img.youtube.com/vi/${id}/hqdefault.jpg` : ''
}
