<script setup>
import { computed } from 'vue'
import { videoThumbnail } from '../lib/video'
import { orgLogo } from '../lib/logos'

const props = defineProps({
  person: { type: Object, required: true },
})

const thumb = computed(() => videoThumbnail(props.person.video) || '/btb-cover.png')
const logo = computed(() => orgLogo(props.person.org))

// Hide a logo that fails to load rather than showing a broken image.
function hideBroken(e) {
  e.target.style.display = 'none'
}
</script>

<template>
  <router-link :to="`/interviews/${person.id}`" class="card">
    <div class="thumb">
      <img
        :src="thumb"
        :alt="`${person.name} — ${person.org} interview`"
        loading="lazy"
        width="480"
        height="270"
      />
      <span class="ep-badge meta">EP {{ String(person.episode).padStart(2, '0') }}</span>
      <span class="play" aria-hidden="true">
        <svg viewBox="0 0 24 24" width="20" height="20"><path d="M8 5v14l11-7z" fill="currentColor" /></svg>
      </span>
    </div>

    <div class="body">
      <span class="field meta">{{ person.field }}</span>
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
        <span>{{ person.role }} · {{ person.org }}</span>
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
  background: #fff;
  overflow: hidden;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}

.card:hover {
  border-color: var(--border-strong);
  transform: translateY(-3px);
  box-shadow: 0 10px 28px rgba(20, 22, 26, 0.09);
}

/* thumbnail */
.thumb {
  position: relative;
  aspect-ratio: 16 / 9;
  background: #edeef0;
  overflow: hidden;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.45s ease;
}

.card:hover .thumb img {
  transform: scale(1.045);
}

.ep-badge {
  position: absolute;
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
