<script setup>
import { computed, ref, watch, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { interviews, getInterview } from '../data/interviews'
import { loadTranscript } from '../data/transcript'
import { useSeo } from '../composables/useSeo'
import { useI18n } from '../composables/useI18n'
import { interviewSeo } from '../lib/seo'
import { orgLogo } from '../lib/logos'
import ChatPanel from '../components/ChatPanel.vue'
import VideoEmbed from '../components/VideoEmbed.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const router = useRouter()
const { t, tc } = useI18n()
const person = computed(() => getInterview(props.id))

// Full transcript — lazily loaded per episode. Kept in the DOM (inside <details>)
// so search engines index the text even while it's visually collapsed.
const transcript = ref([])
watch(
  () => props.id,
  async (id) => {
    transcript.value = await loadTranscript(id)
  },
  { immediate: true }
)

const neighbors = computed(() => {
  const i = interviews.findIndex((p) => p.id === props.id)
  return {
    prev: i > 0 ? interviews[i - 1] : null,
    next: i >= 0 && i < interviews.length - 1 ? interviews[i + 1] : null,
  }
})

watchEffect(() => {
  if (!person.value) router.replace('/')
})

useSeo(() => (person.value ? interviewSeo(person.value) : null))
</script>

<template>
  <main v-if="person" class="detail">
    <div class="detail-hero">
      <div class="container">
        <router-link :to="{ path: '/', hash: '#interviews' }" class="back">
          ← {{ t('interview.back') }}
        </router-link>

        <header class="head">
          <p class="meta head-meta" v-reveal>
            EP {{ String(person.episode).padStart(2, '0') }} · {{ tc(person, 'field') }}
          </p>
          <h1 v-reveal="50">{{ person.name }}</h1>
          <p class="byline" v-reveal="90">
            <img
              v-if="orgLogo(person.org)"
              class="org-logo"
              :src="orgLogo(person.org)"
              :alt="`${person.org} logo`"
              width="22"
              height="22"
              @error="(e) => (e.target.style.display = 'none')"
            />
            <span>{{ tc(person, 'role') }} · {{ person.org }}</span>
          </p>
        </header>
      </div>

      <div class="container video-wrap" v-reveal="120">
        <VideoEmbed
          :video="person.video"
          :title="t('interview.videoTitle', { name: person.name })"
          :episode="person.episode"
        />
      </div>
    </div>

    <div class="container detail-grid">
      <!-- main column -->
      <article>
        <section class="bio" v-reveal>
          <h2>{{ t('interview.about') }}</h2>
          <p>{{ tc(person, 'intro') }}</p>
        </section>

        <section class="highlights" v-reveal>
          <h2>{{ t('interview.inEpisode') }}</h2>
          <ol>
            <li v-for="(h, i) in tc(person, 'highlights')" :key="i">
              <span class="hl-num meta">{{ String(i + 1).padStart(2, '0') }}</span>
              <span>{{ h }}</span>
            </li>
          </ol>
        </section>

        <blockquote class="quote" v-reveal>
          <p>“{{ tc(person, 'quote') }}”</p>
          <cite>{{ person.name }}</cite>
        </blockquote>

        <section v-if="transcript.length" class="transcript" v-reveal>
          <details class="ts">
            <summary class="ts-summary">
              <h2>{{ t('interview.transcript') }}</h2>
              <span class="ts-hint meta">{{ t('interview.transcriptHint', { n: transcript.length }) }}</span>
            </summary>
            <div class="ts-body">
              <p v-for="(para, i) in transcript" :key="i">{{ para }}</p>
            </div>
          </details>
        </section>

        <nav class="pager" :aria-label="t('interview.moreEpisodes')" v-reveal>
          <router-link
            v-if="neighbors.prev"
            :to="`/interviews/${neighbors.prev.id}`"
            class="pager-link"
          >
            ← {{ neighbors.prev.name }}
          </router-link>
          <span v-else></span>
          <router-link
            v-if="neighbors.next"
            :to="`/interviews/${neighbors.next.id}`"
            class="pager-link"
          >
            {{ neighbors.next.name }} →
          </router-link>
        </nav>
      </article>

      <!-- sidebar -->
      <aside>
        <div class="side-sticky">
          <ChatPanel variant="sidebar" :suggestions="person.questions" />
        </div>
      </aside>
    </div>
  </main>
</template>

<style scoped>
.detail {
  padding-bottom: 96px;
}

/* cinematic hero: header + full-width video over a soft aura */
.detail-hero {
  position: relative;
  padding-top: calc(var(--nav-h) + 40px);
}

.detail-hero::before {
  content: '';
  position: absolute;
  top: -6%;
  left: 50%;
  width: 900px;
  max-width: 94%;
  height: 460px;
  transform: translateX(-50%);
  background: radial-gradient(ellipse at center, rgba(91, 130, 255, 0.15), transparent 66%);
  filter: blur(26px);
  z-index: 0;
  pointer-events: none;
}

.detail-hero .container {
  position: relative;
  z-index: 1;
}

.video-wrap {
  margin-top: 30px;
}

.video-wrap :deep(.player) {
  box-shadow: 0 24px 60px rgba(20, 22, 26, 0.14);
}

:root[data-theme='dark'] .video-wrap :deep(.player) {
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.55);
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 56px;
  align-items: start;
  margin-top: 56px;
}

/* video no longer leads the article — don't push the first section down */
.detail-grid article > :first-child {
  margin-top: 0;
}

/* header */
.back {
  display: inline-block;
  color: var(--faint);
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 28px;
  transition: color 0.2s ease;
}

.back:hover {
  color: var(--text);
}

.head-meta {
  margin-bottom: 6px;
}

h1 {
  font-size: clamp(26px, 3.2vw, 34px);
  font-weight: 700;
  letter-spacing: -0.025em;
}

.byline {
  display: flex;
  align-items: center;
  gap: 9px;
  margin-top: 8px;
  font-size: 15px;
  color: var(--muted);
}

.org-logo {
  width: 22px;
  height: 22px;
  flex: none;
  border-radius: 5px;
  object-fit: contain;
}

/* bio */
.bio,
.highlights {
  margin-top: 48px;
}

.bio h2,
.highlights h2 {
  font-size: 20px;
  font-weight: 650;
  margin-bottom: 14px;
}

.bio p {
  color: var(--muted);
  font-size: 15.5px;
  line-height: 1.75;
  max-width: 620px;
}

/* highlights */
.highlights ol {
  list-style: none;
}

.highlights li {
  display: flex;
  gap: 16px;
  align-items: baseline;
  padding: 13px 2px;
  border-bottom: 1px solid var(--border);
  font-size: 15px;
}

.hl-num {
  flex: none;
}

/* quote */
.quote {
  margin-top: 48px;
  padding-left: 22px;
  border-left: 2px solid var(--ink);
}

.quote p {
  font-size: 19px;
  font-weight: 550;
  letter-spacing: -0.01em;
  line-height: 1.45;
  max-width: 560px;
}

.quote cite {
  display: block;
  margin-top: 10px;
  font-style: normal;
  font-size: 13.5px;
  color: var(--faint);
}

/* transcript */
.transcript {
  margin-top: 48px;
}

.ts {
  border-top: 1px solid var(--border);
  padding-top: 8px;
}

.ts-summary {
  list-style: none;
  cursor: pointer;
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 6px 14px;
  padding: 12px 0;
}

.ts-summary::-webkit-details-marker {
  display: none;
}

.ts-summary h2 {
  font-size: 20px;
  font-weight: 650;
  display: inline;
}

.ts-summary h2::before {
  content: '＋';
  margin-right: 10px;
  color: var(--faint);
  font-weight: 400;
}

.ts[open] .ts-summary h2::before {
  content: '－';
}

.ts-hint {
  font-size: 12.5px;
}

.ts-body {
  margin-top: 8px;
  max-width: 660px;
}

.ts-body p {
  color: var(--muted);
  font-size: 15px;
  line-height: 1.8;
  margin-bottom: 16px;
}

/* pager */
.pager {
  margin-top: 56px;
  padding-top: 24px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  gap: 16px;
}

.pager-link {
  font-size: 14.5px;
  font-weight: 550;
  color: var(--muted);
  transition: color 0.2s ease;
}

.pager-link:hover {
  color: var(--text);
}

/* sidebar */
.side-sticky {
  position: sticky;
  top: calc(var(--nav-h) + 24px);
}

@media (max-width: 1000px) {
  .detail-grid {
    grid-template-columns: 1fr;
    gap: 48px;
  }
  .side-sticky {
    position: static;
  }
}
</style>
