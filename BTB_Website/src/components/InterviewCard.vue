<script setup>
import { computed } from 'vue'
import { videoThumbnailHi, videoThumbnailMq } from '../lib/video'
import { orgLogo } from '../lib/logos'
import { useI18n } from '../composables/useI18n'

const { tc, locale } = useI18n()

const props = defineProps({
  person: { type: Object, required: true },
})

// Upload date, formatted in the active language and pinned to the intended
// calendar day regardless of the viewer's timezone.
function formatDate(iso) {
  if (!iso) return ''
  const [y, m, d] = iso.slice(0, 10).split('-').map(Number)
  return new Date(Date.UTC(y, m - 1, d)).toLocaleDateString(locale.value, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    timeZone: 'UTC',
  })
}

const thumb = computed(() => videoThumbnailHi(props.person.video) || '/btb-cover.png')
const thumbMq = computed(() => videoThumbnailMq(props.person.video))
const logo = computed(() => orgLogo(props.person.org))

// Hide a logo that fails to load rather than showing a broken image.
function hideBroken(e) {
  e.target.style.display = 'none'
}

// maxresdefault isn't guaranteed: YouTube may 404 or serve a 120x90 gray
// placeholder. Detect either (error, or a tiny naturalWidth) and fall back to
// the always-present, bar-free mqdefault.
function onThumb(e) {
  const img = e.target
  if (img.dataset.fallback) return
  if (e.type === 'error' || img.naturalWidth <= 120) {
    img.dataset.fallback = '1'
    if (thumbMq.value) img.src = thumbMq.value
  }
}
</script>

<template>
  <router-link :to="`/interviews/${person.id}`" class="card">
    <div class="thumb">
      <img
        :src="thumb"
        :alt="`${person.name}, ${person.org} interview`"
        loading="lazy"
        width="480"
        height="270"
        @load="onThumb"
        @error="onThumb"
      />
      <span class="ep-badge meta">EP {{ String(person.episode).padStart(2, '0') }}</span>
      <span class="play" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="20" height="20"><path d="M8 5v14l11-7z" fill="currentColor" /></svg>
      </span>
    </div>

    <div class="body">
      <span class="field meta">{{ tc(person, 'field')
        }}<span v-if="person.date"> · {{ formatDate(person.date) }}</span></span>
      <h3>{{ person.name }}</h3>
      <p class="role">
        <img
          v-if="logo"
          class="logo"
          :src="logo"
          :alt="`${person.org} logo`"
          width="18"
          height="18"
          loading="lazy"
          @error="hideBroken"
        />
        <span>{{ tc(person, 'role') }} · {{ person.org }}</span>
      </p>
    </div>
  </router-link>
</template>

<style scoped>
.card {
  position: relative;
  display: flex;
  flex-direction: column;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: var(--card);
  overflow: hidden;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}

.card:hover {
  border-color: var(--border-strong);
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(20, 22, 26, 0.09);
}

:root[data-theme='dark'] .card:hover {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(91, 130, 255, 0.15);
}

/* thumbnail */
.thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  background: var(--surface);
  overflow: hidden;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  /* slight over-crop hides any thin letterbox sliver at the edges */
  transform: scale(1.02);
  transition: transform 0.45s ease;
}

.card:hover .thumb img {
  transform: scale(1.06);
}

.thumb::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(to top, rgba(10, 12, 18, 0.28), transparent 45%);
  pointer-events: none;
}

.ep-badge {
  position: absolute;
  z-index: 2;
  top: 10px;
  left: 10px;
  background: rgba(15, 17, 20, 0.66);
  color: #fff;
  padding: 3px 8px;
  border-radius: 6px;
  font-size: 11px;
  letter-spacing: 0.04em;
}

.play {
  position: absolute;
  z-index: 2;
  inset: 0;
  margin: auto;
  width: 52px;
  height: 52px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(15, 17, 20, 0.55);
  color: #fff;
  opacity: 0.85;
  transform: scale(0.92);
  transition: opacity 0.25s ease, transform 0.25s ease, background 0.25s ease;
}

.play svg {
  margin-left: 3px;
}

.card:hover .play {
  opacity: 1;
  transform: scale(1);
  background: var(--accent);
}

/* body */
.body {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 15px 20px 20px;
}

.field {
  font-size: 11.5px;
}

h3 {
  font-size: 17px;
  font-weight: 650;
  letter-spacing: -0.01em;
}

.role {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 3px;
  color: var(--muted);
  font-size: 13.5px;
}

.logo {
  width: 18px;
  height: 18px;
  flex: none;
  border-radius: 4px;
  object-fit: contain;
  background: #fff;
}

@media (prefers-reduced-motion: reduce) {
  .thumb img,
  .card,
  .play {
    transition: none;
  }
}
</style>
