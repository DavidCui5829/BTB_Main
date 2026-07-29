<script setup>
import { computed } from 'vue'
import { videoThumbnailHi, videoThumbnailMq } from '../lib/video'
import { orgLogo } from '../lib/logos'
import { useI18n } from '../composables/useI18n'

const { t, tc } = useI18n()

const props = defineProps({
  person: { type: Object, required: true },
})

const thumb = computed(() => videoThumbnailHi(props.person.video) || '/btb-cover.png')
const thumbMq = computed(() => videoThumbnailMq(props.person.video))
const logo = computed(() => orgLogo(props.person.org))

function hideBroken(e) {
  e.target.style.display = 'none'
}

// maxresdefault may 404 or serve a 120x90 gray placeholder — fall back to mqdefault.
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
  <router-link :to="`/interviews/${person.id}`" class="feature">
    <div class="feature-thumb">
      <img
        :src="thumb"
        :alt="`${person.name}, ${person.org} interview`"
        loading="lazy"
        width="640"
        height="360"
        @load="onThumb"
        @error="onThumb"
      />
      <span class="feature-badge">◆ {{ t('featured.latest') }} · EP {{ String(person.episode).padStart(2, '0') }}</span>
      <span class="play" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="24" height="24"><path d="M8 5v14l11-7z" fill="currentColor" /></svg>
      </span>
    </div>

    <div class="feature-body">
      <span class="feature-field meta">{{ tc(person, 'field') }}</span>
      <h3>{{ person.name }}</h3>
      <p class="feature-role">
        <img
          v-if="logo"
          class="logo"
          :src="logo"
          :alt="`${person.org} logo`"
          width="20"
          height="20"
          loading="lazy"
          @error="hideBroken"
        />
        <span>{{ tc(person, 'role') }} · {{ person.org }}</span>
      </p>
      <p class="feature-intro">{{ tc(person, 'intro') }}</p>
      <span class="feature-cta">{{ t('featured.watch') }} →</span>
    </div>
  </router-link>
</template>

<style scoped>
.feature {
  display: grid;
  grid-template-columns: 1.15fr 1fr;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--card);
  overflow: hidden;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}

.feature:hover {
  border-color: var(--border-strong);
  transform: translateY(-3px);
  box-shadow: 0 16px 44px rgba(20, 22, 26, 0.12);
}

:root[data-theme='dark'] .feature:hover {
  box-shadow: 0 16px 44px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(91, 130, 255, 0.18);
}

.feature-thumb {
  position: relative;
  min-height: 280px;
  background: var(--surface);
  overflow: hidden;
}

.feature-thumb img {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.02);
  transition: transform 0.5s ease;
}

.feature:hover .feature-thumb img {
  transform: scale(1.06);
}

.feature-thumb::after {
  content: '';
  position: absolute;
  inset: 0;
  z-index: 1;
  background: linear-gradient(120deg, transparent 58%, rgba(10, 12, 18, 0.26));
  pointer-events: none;
}

.feature-badge {
  position: absolute;
  z-index: 2;
  top: 14px;
  left: 14px;
  background: var(--accent);
  color: #fff;
  padding: 5px 11px;
  border-radius: 8px;
  font-size: 11.5px;
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.play {
  position: absolute;
  z-index: 2;
  inset: 0;
  margin: auto;
  width: 60px;
  height: 60px;
  display: grid;
  place-items: center;
  border-radius: 50%;
  background: rgba(15, 17, 20, 0.55);
  color: #fff;
  opacity: 0.9;
  transform: scale(0.94);
  transition: opacity 0.25s ease, transform 0.25s ease, background 0.25s ease;
}

.play svg {
  margin-left: 3px;
}

.feature:hover .play {
  opacity: 1;
  transform: scale(1);
  background: var(--accent);
}

.feature-body {
  padding: 30px 34px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 5px;
}

.feature-field {
  font-size: 11.5px;
}

.feature-body h3 {
  font-size: clamp(22px, 2.6vw, 28px);
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-top: 6px;
}

.feature-role {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
  color: var(--muted);
  font-size: 14.5px;
}

.logo {
  width: 20px;
  height: 20px;
  flex: none;
  border-radius: 4px;
  object-fit: contain;
  background: #fff;
}

.feature-intro {
  margin-top: 10px;
  color: var(--muted);
  font-size: 14.5px;
  line-height: 1.7;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.feature-cta {
  margin-top: 16px;
  color: var(--accent);
  font-weight: 600;
  font-size: 14.5px;
}

.feature:hover .feature-cta {
  color: var(--accent-hover);
}

@media (max-width: 760px) {
  .feature {
    grid-template-columns: 1fr;
  }
  .feature-thumb {
    aspect-ratio: 16 / 9;
    min-height: 0;
  }
  .feature-body {
    padding: 22px 22px 24px;
  }
}

@media (prefers-reduced-motion: reduce) {
  .feature,
  .feature-thumb img,
  .play {
    transition: none;
  }
}
</style>
