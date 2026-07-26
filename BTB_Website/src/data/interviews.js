// One entry per Beyond the Blueprint episode.
//
// The data lives in interviews.json so the BTB_AI backend's admin endpoints
// can read and write it (see the unlisted /admin page). Edit it there or by
// hand — array order is the display order on the site.
//
// `video` accepts a YouTube link (any format) or a file in /public
// (e.g. '/videos/XavierEldridge.mp4'). Leave '' for a placeholder.
//
// `ragId` must match the interview id used by the BTB_AI backend
// (the folder names in BTB_Prepare).

import interviews from './interviews.json'

export { interviews }

export function getInterview(id) {
  return interviews.find((p) => p.id === id)
}

export function getByRagId(ragId) {
  return interviews.find((p) => p.ragId === ragId)
}
