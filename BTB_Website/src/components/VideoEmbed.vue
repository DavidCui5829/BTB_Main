<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()

const props = defineProps({
  video: { type: String, default: '' },
  title: { type: String, required: true },
  episode: { type: Number, required: true },
})

const kind = computed(() => {
  if (!props.video) return 'none'
  if (/youtube\.com|youtu\.be/.test(props.video)) return 'youtube'
  return 'file'
})

const embedUrl = computed(() => {
  const m = props.video.match(
    /(?:youtube\.com\/(?:watch\?v=|embed\/|shorts\/)|youtu\.be\/)([\w-]{6,})/
  )
  return m ? `https://www.youtube.com/embed/${m[1]}` : props.video
})
</script>

<template>
  <div class="player">
    <iframe
      v-if="kind === 'youtube'"
      :src="embedUrl"
      :title="title"
      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
      allowfullscreen
    ></iframe>

    <video v-else-if="kind === 'file'" :src="video" controls preload="metadata"></video>

    <div v-else class="placeholder">
      <span class="meta">EP {{ String(episode).padStart(2, '0') }}</span>
      <p>{{ t('video.comingSoon') }}</p>
    </div>
  </div>
</template>

<style scoped>
.player {
  position: relative;
  aspect-ratio: 16 / 9;
  border-radius: var(--radius-lg);
  overflow: hidden;
  border: 1px solid var(--border);
  background: var(--surface);
}

iframe,
video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  border: 0;
  object-fit: contain;
  background: #000;
}

.placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.placeholder p {
  font-weight: 550;
  font-size: 16px;
  color: var(--muted);
}
</style>
