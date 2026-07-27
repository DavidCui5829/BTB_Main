<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { onBeforeRouteLeave } from 'vue-router'

// Unlisted admin console. Loads the interview catalog from the BTB_AI backend
// and saves the full list back — the backend writes src/data/interviews.json,
// which the site imports, so the Vite dev server hot-reloads changes live.

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'
const TOKEN_KEY = 'btb-admin-token'

const token = ref(localStorage.getItem(TOKEN_KEY) || '')

function rememberToken() {
  try {
    localStorage.setItem(TOKEN_KEY, token.value)
  } catch {
    /* private mode — token just won't persist */
  }
}

const items = ref([])
const loadState = ref('loading') // 'loading' | 'ready' | 'error'
const loadError = ref('')
const saveState = ref('idle') // 'idle' | 'saving' | 'saved' | 'error'
const saveError = ref('')
const savedSnapshot = ref('')
const expanded = ref(new Set())

let uid = 0
const withKey = (data) => ({ _key: `k${uid++}`, ...data })
const stripKey = ({ _key, ...rest }) => rest

const serialize = (list) => JSON.stringify(list.map(stripKey))
const dirty = computed(() => loadState.value === 'ready' && serialize(items.value) !== savedSnapshot.value)

const START_BACKEND_HINT =
  `Can't reach the backend at ${API_BASE}. From the BTB_AI folder run: ` +
  'python -m uvicorn app.main:app --port 8000'

async function load() {
  if (dirty.value && !window.confirm('Reload from disk and discard your unsaved changes?')) return
  loadState.value = 'loading'
  loadError.value = ''
  try {
    const res = await fetch(`${API_BASE}/admin/interviews`)
    if (!res.ok) throw new Error(`The backend returned an error (${res.status}).`)
    const data = await res.json()
    items.value = data.map(withKey)
    savedSnapshot.value = serialize(items.value)
    saveState.value = 'idle'
    loadState.value = 'ready'
  } catch (err) {
    loadError.value = err instanceof TypeError ? START_BACKEND_HINT : err.message
    loadState.value = 'error'
  }
}

async function save() {
  if (saveState.value === 'saving' || loadState.value !== 'ready') return
  saveState.value = 'saving'
  saveError.value = ''
  rememberToken()
  try {
    const res = await fetch(`${API_BASE}/admin/interviews`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json', 'X-Admin-Token': token.value },
      body: JSON.stringify(items.value.map(stripKey)),
    })
    if (!res.ok) {
      const detail = await res
        .json()
        .then((d) => {
          if (typeof d.detail === 'string') return d.detail
          if (Array.isArray(d.detail)) {
            return d.detail
              .map((e) => {
                const where = (e.loc || []).slice(1).join(' → ')
                return where ? `${where}: ${e.msg}` : e.msg
              })
              .join(' · ')
          }
          return null
        })
        .catch(() => null)
      throw new Error(detail || `Save failed (${res.status}).`)
    }
    savedSnapshot.value = serialize(items.value)
    saveState.value = 'saved'
    setTimeout(() => {
      if (saveState.value === 'saved') saveState.value = 'idle'
    }, 3000)
  } catch (err) {
    saveError.value = err instanceof TypeError ? START_BACKEND_HINT : err.message
    saveState.value = 'error'
  }
}

function addInterview() {
  const episode = items.value.reduce((max, p) => Math.max(max, Number(p.episode) || 0), 0) + 1
  const item = withKey({
    id: '',
    ragId: '',
    episode,
    name: '',
    role: '',
    org: '',
    field: '',
    video: '',
    intro: '',
    highlights: [],
    quote: '',
    questions: [],
  })
  items.value.push(item)
  expanded.value.add(item._key)
  nextTick(() => {
    document.getElementById(`card-${item._key}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })
  })
}

function removeInterview(i) {
  const name = items.value[i].name || 'this interview'
  if (!window.confirm(`Delete “${name}”? It disappears from the site when you save.`)) return
  expanded.value.delete(items.value[i]._key)
  items.value.splice(i, 1)
}

function move(i, delta) {
  const j = i + delta
  if (j < 0 || j >= items.value.length) return
  const list = items.value
  ;[list[i], list[j]] = [list[j], list[i]]
}

function toggle(key) {
  if (expanded.value.has(key)) expanded.value.delete(key)
  else expanded.value.add(key)
}

// Textareas edit highlights/questions as one entry per line (applied on blur).
const toLines = (arr) => arr.join('\n')
const fromLines = (text) =>
  text
    .split('\n')
    .map((s) => s.trim())
    .filter(Boolean)

function slugify(s) {
  return s
    .toLowerCase()
    .normalize('NFKD')
    .replace(/[̀-ͯ]/g, '')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
}

function suggestId(item) {
  if (!item.id && item.name) item.id = slugify(item.name)
}

function onBeforeUnload(e) {
  if (dirty.value) {
    e.preventDefault()
    e.returnValue = ''
  }
}

onBeforeRouteLeave(() => {
  if (dirty.value && !window.confirm('You have unsaved changes. Leave anyway?')) return false
})

onMounted(() => {
  document.title = 'Admin | Beyond the Blueprint'
  window.addEventListener('beforeunload', onBeforeUnload)
  load()
})

onBeforeUnmount(() => window.removeEventListener('beforeunload', onBeforeUnload))
</script>

<template>
  <main class="admin">
    <div class="container">
      <header class="head">
        <p class="meta">Unlisted · not linked from the site</p>
        <h1>Interview admin</h1>
        <p class="sub">
          Add, edit, reorder, and delete episodes. Saving writes
          <code>src/data/interviews.json</code>; the array order here is the display order on the
          site.
        </p>
      </header>

      <div class="toolbar">
        <label class="token">
          <span>Admin token</span>
          <input
            v-model="token"
            type="password"
            placeholder="required to save"
            autocomplete="off"
            @change="rememberToken"
          />
        </label>
        <div class="toolbar-actions">
          <button class="btn" :disabled="loadState === 'loading'" @click="load">Reload</button>
          <button class="btn" :disabled="loadState !== 'ready'" @click="addInterview">
            + Add interview
          </button>
          <button
            class="btn btn--primary"
            :disabled="!dirty || saveState === 'saving'"
            @click="save"
          >
            {{ saveState === 'saving' ? 'Saving…' : 'Save changes' }}
          </button>
        </div>
      </div>

      <p v-if="saveState === 'error'" class="notice notice--err">{{ saveError }}</p>
      <p v-else-if="saveState === 'saved'" class="notice notice--ok">
        Saved. The site is up to date.
      </p>
      <p v-else-if="dirty" class="notice notice--dirty">
        Unsaved changes. Nothing touches the site until you press “Save changes”.
      </p>

      <div v-if="loadState === 'loading'" class="empty">Loading interviews…</div>

      <div v-else-if="loadState === 'error'" class="empty">
        <p>{{ loadError }}</p>
        <button class="btn" @click="load">Try again</button>
      </div>

      <ul v-else class="cards">
        <li v-for="(item, i) in items" :id="`card-${item._key}`" :key="item._key" class="card">
          <div class="card-row">
            <button
              class="card-toggle"
              :aria-expanded="expanded.has(item._key)"
              @click="toggle(item._key)"
            >
              <span class="meta ep">EP {{ String(item.episode || 0).padStart(2, '0') }}</span>
              <strong>{{ item.name || 'New interview' }}</strong>
              <span class="card-sub">{{ [item.role, item.org].filter(Boolean).join(' · ') }}</span>
              <span class="chevron" :class="{ open: expanded.has(item._key) }">▾</span>
            </button>
            <div class="card-actions">
              <button class="icon-btn" title="Move up" :disabled="i === 0" @click="move(i, -1)">
                ↑
              </button>
              <button
                class="icon-btn"
                title="Move down"
                :disabled="i === items.length - 1"
                @click="move(i, 1)"
              >
                ↓
              </button>
              <button class="icon-btn danger" @click="removeInterview(i)">Delete</button>
            </div>
          </div>

          <div v-if="expanded.has(item._key)" class="card-form">
            <label class="f f--grow">
              <span>Name</span>
              <input v-model="item.name" @blur="suggestId(item)" />
            </label>
            <label class="f f--xs">
              <span>Episode</span>
              <input v-model.number="item.episode" type="number" min="1" />
            </label>

            <label class="f">
              <span>Role</span>
              <input v-model="item.role" placeholder="e.g. Software Engineer" />
            </label>
            <label class="f">
              <span>Organization</span>
              <input v-model="item.org" placeholder="e.g. Google" />
            </label>

            <label class="f">
              <span>Field <em>shown as the episode tag</em></span>
              <input v-model="item.field" placeholder="e.g. Aerospace" />
            </label>
            <label class="f">
              <span>Video <em>YouTube URL or /videos/File.mp4 (blank for placeholder)</em></span>
              <input v-model="item.video" />
            </label>

            <label class="f">
              <span>URL id <em>lowercase-with-hyphens, used in /interviews/…</em></span>
              <input v-model="item.id" placeholder="e.g. jane-doe" />
            </label>
            <label class="f">
              <span>RAG id <em>must match the BTB_AI folder name</em></span>
              <input v-model="item.ragId" placeholder="e.g. JaneDoe" />
            </label>

            <label class="f f--full">
              <span>Intro paragraph</span>
              <textarea v-model="item.intro" rows="4"></textarea>
            </label>

            <label class="f f--full">
              <span>Pull quote</span>
              <textarea v-model="item.quote" rows="2"></textarea>
            </label>

            <label class="f f--half">
              <span>Episode highlights <em>one per line</em></span>
              <textarea
                :value="toLines(item.highlights)"
                rows="5"
                @change="item.highlights = fromLines($event.target.value)"
              ></textarea>
            </label>
            <label class="f f--half">
              <span>Suggested questions <em>one per line, shown in the chat</em></span>
              <textarea
                :value="toLines(item.questions)"
                rows="5"
                @change="item.questions = fromLines($event.target.value)"
              ></textarea>
            </label>
          </div>
        </li>
      </ul>
    </div>
  </main>
</template>

<style scoped>
.admin {
  padding: calc(var(--nav-h) + 48px) 0 96px;
  flex: 1;
}

.head .sub {
  margin-top: 8px;
  color: var(--muted);
  font-size: 15px;
  max-width: 560px;
}

.head code {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 1px 6px;
  font-size: 13px;
}

h1 {
  margin-top: 6px;
  font-size: clamp(26px, 3.2vw, 34px);
  font-weight: 700;
  letter-spacing: -0.025em;
}

/* toolbar */
.toolbar {
  margin-top: 28px;
  display: flex;
  flex-wrap: wrap;
  align-items: flex-end;
  gap: 14px;
  padding: 16px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: #fff;
}

.token {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-right: auto;
}

.token span {
  font-size: 12.5px;
  font-weight: 550;
  color: var(--muted);
}

.token input {
  width: 220px;
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: var(--bg);
  font-size: 14px;
}

.toolbar-actions {
  display: flex;
  gap: 8px;
}

.btn {
  padding: 10px 16px;
  border-radius: 10px;
  border: 1px solid var(--border-strong);
  background: #fff;
  font-size: 14px;
  font-weight: 550;
  transition: border-color 0.2s ease, background 0.2s ease, opacity 0.2s ease;
}

.btn:hover:not(:disabled) {
  border-color: var(--faint);
}

.btn--primary {
  background: var(--ink);
  border-color: var(--ink);
  color: #fff;
}

.btn--primary:hover:not(:disabled) {
  background: #000;
}

.btn:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

/* notices */
.notice {
  margin-top: 14px;
  padding: 10px 14px;
  border-radius: 10px;
  font-size: 13.5px;
  border: 1px solid var(--border);
}

.notice--dirty {
  background: #fdf8ec;
  border-color: #f0e3bb;
  color: #8a6d1f;
}

.notice--ok {
  background: #f0f9f1;
  border-color: #cfe8d2;
  color: #2f7d3b;
}

.notice--err {
  background: #fdf2f2;
  border-color: #f3d4d4;
  color: #a04545;
}

/* empty / loading */
.empty {
  margin-top: 48px;
  text-align: center;
  color: var(--muted);
  font-size: 15px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 14px;
}

/* cards */
.cards {
  list-style: none;
  margin-top: 22px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card {
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: #fff;
  overflow: hidden;
}

.card-row {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-right: 10px;
}

.card-toggle {
  flex: 1;
  display: flex;
  align-items: baseline;
  gap: 12px;
  padding: 15px 18px;
  text-align: left;
  min-width: 0;
}

.card-toggle strong {
  font-size: 15.5px;
  font-weight: 650;
  white-space: nowrap;
}

.ep {
  flex: none;
}

.card-sub {
  color: var(--faint);
  font-size: 13.5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chevron {
  margin-left: auto;
  color: var(--faint);
  transition: transform 0.2s ease;
}

.chevron.open {
  transform: rotate(180deg);
}

.card-actions {
  display: flex;
  gap: 4px;
  flex: none;
}

.icon-btn {
  padding: 7px 10px;
  border-radius: 8px;
  font-size: 13px;
  color: var(--muted);
  border: 1px solid transparent;
  transition: border-color 0.2s ease, color 0.2s ease, background 0.2s ease;
}

.icon-btn:hover:not(:disabled) {
  border-color: var(--border-strong);
  color: var(--text);
}

.icon-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}

.icon-btn.danger:hover:not(:disabled) {
  background: #fdf2f2;
  border-color: #f3d4d4;
  color: #a04545;
}

/* form */
.card-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 14px 16px;
  padding: 18px;
  border-top: 1px solid var(--border);
  background: var(--bg);
}

.f {
  display: flex;
  flex-direction: column;
  gap: 5px;
  min-width: 0;
}

.f--grow {
  grid-column: 1;
}

.f--xs input {
  width: 110px;
}

.f--full {
  grid-column: 1 / -1;
}

.f span {
  font-size: 12.5px;
  font-weight: 550;
  color: var(--muted);
}

.f span em {
  font-style: normal;
  font-weight: 400;
  color: var(--faint);
}

.f input,
.f textarea {
  padding: 9px 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  background: #fff;
  font-size: 14px;
  line-height: 1.5;
  transition: border-color 0.2s ease;
}

.f textarea {
  resize: vertical;
}

.f input:focus,
.f textarea:focus {
  outline: none;
  border-color: var(--border-strong);
}

@media (max-width: 720px) {
  .card-form {
    grid-template-columns: 1fr;
  }
  .f--half,
  .f--grow {
    grid-column: auto;
  }
  .token input {
    width: 100%;
  }
  .toolbar-actions {
    width: 100%;
    flex-wrap: wrap;
  }
}
</style>
