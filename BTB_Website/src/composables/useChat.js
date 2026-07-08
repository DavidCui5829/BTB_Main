import { reactive, watch } from 'vue'

// One shared conversation for the whole site: the chat on the homepage and the
// sidebar chat on every interview page read and write the same history, and it
// survives reloads via localStorage.

// 127.0.0.1 (not localhost) — uvicorn binds IPv4 only by default, and Windows
// resolves localhost to ::1 first for some clients.
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const STORAGE_KEY = 'btb-chat-v1'

function loadSaved() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw)
    if (!Array.isArray(data.messages)) return null
    return data
  } catch {
    return null
  }
}

const saved = loadSaved()

const state = reactive({
  sessionId: saved?.sessionId ?? null,
  messages: saved?.messages ?? [],
  pending: false,
})

watch(
  () => [state.messages.length, state.sessionId],
  () => {
    try {
      localStorage.setItem(
        STORAGE_KEY,
        JSON.stringify({ sessionId: state.sessionId, messages: state.messages })
      )
    } catch {
      /* storage full or unavailable — chat still works for the session */
    }
  }
)

let uid = 0
const nextId = () => `m${Date.now()}-${uid++}`

function dedupeSources(sources = []) {
  const seen = new Set()
  const out = []
  for (const s of sources) {
    const key = `${s.interview}::${s.topic}`
    if (seen.has(key)) continue
    seen.add(key)
    out.push({ interview: s.interview, topic: s.topic })
  }
  return out.slice(0, 5)
}

async function send(question) {
  const q = question.trim()
  if (!q || state.pending) return

  state.messages.push({ id: nextId(), role: 'user', text: q })
  state.pending = true

  try {
    const res = await fetch(`${API_BASE}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: q,
        session_id: state.sessionId || undefined,
      }),
    })

    if (!res.ok) {
      const detail = await res
        .json()
        .then((d) => d.detail)
        .catch(() => null)
      throw new Error(detail || `The assistant returned an error (${res.status}).`)
    }

    const data = await res.json()
    state.sessionId = data.session_id
    state.messages.push({
      id: nextId(),
      role: 'assistant',
      text: data.answer,
      sources: dedupeSources(data.sources),
    })
  } catch (err) {
    const offline = err instanceof TypeError // fetch network failure
    state.messages.push({
      id: nextId(),
      role: 'assistant',
      error: true,
      text: offline
        ? `Can't reach the assistant at ${API_BASE}. Start the backend, then ask again.`
        : `Something went wrong: ${err.message}`,
    })
  } finally {
    state.pending = false
  }
}

function clear() {
  const sid = state.sessionId
  state.messages.splice(0, state.messages.length)
  state.sessionId = null
  if (sid) {
    fetch(`${API_BASE}/chat/${sid}`, { method: 'DELETE' }).catch(() => {})
  }
}

export function useChat() {
  return { state, send, clear }
}
