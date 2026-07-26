// Lazy per-episode transcript loader. import.meta.glob makes each transcript its
// own chunk, so the main bundle stays lean — only the viewed episode's transcript
// is fetched, on demand. Files are generated from the diarized recordings; see
// the transcripts/ folder (committed with the site so server rebuilds work).
const loaders = import.meta.glob('./transcripts/*.json')

export async function loadTranscript(id) {
  const loader = loaders[`./transcripts/${id}.json`]
  if (!loader) return []
  const mod = await loader()
  return (mod.default || mod).paragraphs || []
}
