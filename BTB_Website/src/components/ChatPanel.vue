<script setup>
import { nextTick, onMounted, ref, watch } from 'vue'
import { useChat } from '../composables/useChat'
import { displayName, renderLite } from '../lib/format'

defineProps({
  variant: { type: String, default: 'panel' }, // 'panel' | 'sidebar'
  suggestions: { type: Array, default: () => [] },
})

const { state, send, clear } = useChat()
const draft = ref('')
const bodyEl = ref(null)
const inputEl = ref(null)

function submit() {
  const text = draft.value
  if (!text.trim() || state.pending) return
  draft.value = ''
  autoGrow()
  send(text)
}

function ask(question) {
  if (state.pending) return
  send(question)
}

function onKeydown(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    submit()
  }
}

function autoGrow() {
  const el = inputEl.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = `${Math.min(el.scrollHeight, 130)}px`
}

watch(
  () => [state.messages.length, state.pending],
  async () => {
    await nextTick()
    bodyEl.value?.scrollTo({ top: bodyEl.value.scrollHeight, behavior: 'smooth' })
  }
)

onMounted(() => {
  // Resume mid-conversation: open at the latest message, not the top.
  if (state.messages.length && bodyEl.value) {
    bodyEl.value.scrollTop = bodyEl.value.scrollHeight
  }
})
</script>

<template>
  <div class="chat" :class="`chat--${variant}`">
    <header class="chat-head">
      <span class="ai-badge" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="13" height="13" fill="currentColor">
          <path d="M12 2l2.4 7.6L22 12l-7.6 2.4L12 22l-2.4-7.6L2 12l7.6-2.4z" />
        </svg>
      </span>
      <strong>Personalized AI</strong>
      <span class="ai-sub">Trained on every interview</span>
      <button
        v-if="state.messages.length"
        class="clear-btn"
        title="Clear conversation"
        @click="clear"
      >
        Clear
      </button>
    </header>

    <div ref="bodyEl" class="chat-body">
      <div v-if="!state.messages.length" class="chat-empty">
        <button v-for="q in suggestions" :key="q" @click="ask(q)">{{ q }}</button>
      </div>

      <template v-for="m in state.messages" :key="m.id">
        <div class="msg" :class="[`msg--${m.role}`, { 'msg--error': m.error }]">
          <div class="bubble">
            <span v-if="m.role === 'user'">{{ m.text }}</span>
            <span v-else v-html="renderLite(m.text)"></span>
          </div>
          <details v-if="m.sources?.length" class="sources">
            <summary>{{ m.sources.length }} source{{ m.sources.length > 1 ? 's' : '' }}</summary>
            <ul>
              <li v-for="(s, i) in m.sources" :key="i">
                <strong>{{ displayName(s.interview) }}</strong> · {{ s.topic }}
              </li>
            </ul>
          </details>
        </div>
      </template>

      <div v-if="state.pending" class="msg msg--assistant">
        <div class="bubble typing" aria-label="Assistant is thinking">
          <span></span><span></span><span></span>
        </div>
      </div>
    </div>

    <form class="chat-input" @submit.prevent="submit">
      <textarea
        ref="inputEl"
        v-model="draft"
        rows="1"
        placeholder="Ask anything…"
        @keydown="onKeydown"
        @input="autoGrow"
      ></textarea>
      <button
        type="submit"
        class="send-btn"
        :disabled="state.pending || !draft.trim()"
        aria-label="Send question"
      >
        <svg viewBox="0 0 24 24" width="17" height="17" fill="none" aria-hidden="true">
          <path
            d="M4 12h15m0 0-6-6m6 6-6 6"
            stroke="currentColor"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </form>
  </div>
</template>

<style scoped>
.chat {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--card);
  overflow: hidden;
}

/* gradient accent bar across the top of the panel */
.chat::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent), #8b5cf6 50%, #06b6d4);
  z-index: 2;
}

.chat--panel {
  height: 480px;
}

.chat--sidebar {
  height: min(620px, calc(100vh - 120px));
}

@media (max-width: 720px) {
  .chat--panel {
    height: min(440px, 60vh);
  }
}

/* head */
.chat-head {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
}

.ai-badge {
  display: grid;
  place-items: center;
  width: 22px;
  height: 22px;
  flex: none;
  border-radius: 6px;
  color: #fff;
  background: linear-gradient(135deg, var(--accent), #8b5cf6);
}

.chat-head strong {
  font-size: 14px;
  font-weight: 650;
}

.chat-head .ai-sub {
  font-size: 12.5px;
  color: var(--faint);
}

.clear-btn {
  margin-left: auto;
  font-size: 12.5px;
  font-weight: 500;
  color: var(--faint);
  transition: color 0.2s ease;
}

.clear-btn:hover {
  color: var(--text);
}

/* body */
.chat-body {
  flex: 1;
  overflow-y: auto;
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.chat-empty {
  margin: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  width: 100%;
  max-width: 340px;
}

.chat-empty button {
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--bg);
  color: var(--muted);
  font-size: 13.5px;
  text-align: left;
  transition: border-color 0.2s ease, color 0.2s ease;
}

.chat-empty button:hover {
  border-color: var(--border-strong);
  color: var(--text);
}

/* messages */
.msg {
  display: flex;
  flex-direction: column;
  max-width: 88%;
  animation: msg-in 0.25s ease both;
}

@keyframes msg-in {
  from { opacity: 0; transform: translateY(6px); }
  to { opacity: 1; transform: none; }
}

.msg--user {
  align-self: flex-end;
  align-items: flex-end;
}

.msg--assistant {
  align-self: flex-start;
  align-items: flex-start;
}

.bubble {
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14.5px;
  line-height: 1.55;
  overflow-wrap: anywhere;
}

.msg--user .bubble {
  background: var(--accent);
  color: #fff;
  border-bottom-right-radius: 4px;
}

.msg--assistant .bubble {
  background: var(--surface);
  border-bottom-left-radius: 4px;
}

.msg--error .bubble {
  background: rgba(214, 78, 78, 0.12);
  border: 1px solid rgba(214, 78, 78, 0.3);
  color: #d76b6b;
}

.bubble :deep(code) {
  background: rgba(127, 127, 127, 0.16);
  padding: 1px 6px;
  border-radius: 6px;
  font-size: 13px;
}

/* sources */
.sources {
  margin-top: 5px;
  font-size: 12px;
}

.sources summary {
  cursor: pointer;
  color: var(--faint);
  list-style: none;
  transition: color 0.2s ease;
}

.sources summary:hover {
  color: var(--accent);
}

.sources ul {
  list-style: none;
  margin-top: 6px;
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 6px 12px;
  border-left: 2px solid var(--border-strong);
  color: var(--muted);
}

.sources strong {
  color: var(--text);
  font-weight: 600;
}

/* typing */
.typing {
  display: inline-flex;
  gap: 5px;
  align-items: center;
  padding: 13px 15px;
}

.typing span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--faint);
  animation: blink 1.2s infinite;
}

.typing span:nth-child(2) { animation-delay: 0.15s; }
.typing span:nth-child(3) { animation-delay: 0.3s; }

@keyframes blink {
  0%, 80%, 100% { opacity: 0.3; }
  40% { opacity: 1; }
}

/* input */
.chat-input {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 12px;
  border-top: 1px solid var(--border);
}

.chat-input textarea {
  flex: 1;
  resize: none;
  border: 1px solid transparent;
  background: var(--surface);
  border-radius: 10px;
  padding: 10px 13px;
  font-size: 14.5px;
  line-height: 1.45;
  max-height: 130px;
  transition: border-color 0.2s ease, background 0.2s ease;
}

.chat-input textarea:focus {
  outline: none;
  border-color: var(--border-strong);
  background: var(--card);
}

.chat-input textarea::placeholder {
  color: var(--faint);
}

.send-btn {
  flex: none;
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  background: var(--ink);
  color: #fff;
  transition: background 0.2s ease, opacity 0.2s ease;
}

.send-btn:hover:not(:disabled) {
  background: #000;
}

.send-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* In dark mode the send button becomes a light chip with a dark glyph. */
:root[data-theme='dark'] .send-btn {
  color: #0b0e14;
}
:root[data-theme='dark'] .send-btn:hover:not(:disabled) {
  background: #fff;
}

@media (prefers-reduced-motion: reduce) {
  .typing span,
  .msg {
    animation: none;
  }
}
</style>
