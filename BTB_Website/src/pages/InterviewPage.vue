<script setup>
import { computed, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { interviews, getInterview } from '../data/interviews'
import ChatPanel from '../components/ChatPanel.vue'
import VideoEmbed from '../components/VideoEmbed.vue'

const props = defineProps({
  id: { type: String, required: true },
})

const router = useRouter()
const person = computed(() => getInterview(props.id))

const neighbors = computed(() => {
  const i = interviews.findIndex((p) => p.id === props.id)
  return {
    prev: i > 0 ? interviews[i - 1] : null,
    next: i >= 0 && i < interviews.length - 1 ? interviews[i + 1] : null,
  }
})

watchEffect(() => {
  if (!person.value) {
    router.replace('/')
  } else {
    document.title = `${person.value.name} — Beyond the Blueprint`
  }
})
</script>

<template>
  <main v-if="person" class="detail">
    <div class="container">
      <router-link :to="{ path: '/', hash: '#interviews' }" class="back">
        ← Interviews
      </router-link>

      <header class="head">
        <p class="meta head-meta" v-reveal>
          EP {{ String(person.episode).padStart(2, '0') }} · {{ person.field }}
        </p>
        <h1 v-reveal="50">{{ person.name }}</h1>
        <p class="byline" v-reveal="90">{{ person.role }} · {{ person.org }}</p>
      </header>
    </div>

    <div class="container detail-grid">
      <!-- main column -->
      <article>
        <div v-reveal="120">
          <VideoEmbed
            :video="person.video"
            :title="`Interview with ${person.name}`"
            :episode="person.episode"
          />
        </div>

        <section class="bio" v-reveal>
          <h2>About</h2>
          <p>{{ person.intro }}</p>
        </section>

        <section class="highlights" v-reveal>
          <h2>In this episode</h2>
          <ol>
            <li v-for="(h, i) in person.highlights" :key="i">
              <span class="hl-num meta">{{ String(i + 1).padStart(2, '0') }}</span>
              <span>{{ h }}</span>
            </li>
          </ol>
        </section>

        <blockquote class="quote" v-reveal>
          <p>“{{ person.quote }}”</p>
          <cite>{{ person.name }}</cite>
        </blockquote>

        <nav class="pager" aria-label="More episodes">
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
  padding: calc(var(--nav-h) + 48px) 0 96px;
}

.detail-grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 360px;
  gap: 56px;
  align-items: start;
  margin-top: 36px;
}

/* header */
.back {
  display: inline-block;
  color: var(--faint);
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 36px;
  transition: color 0.2s ease;
}

.back:hover {
  color: var(--text);
}

.head-meta {
  margin-bottom: 10px;
}

h1 {
  font-size: clamp(32px, 4.5vw, 44px);
  font-weight: 700;
  letter-spacing: -0.025em;
}

.byline {
  margin-top: 8px;
  font-size: 16px;
  color: var(--muted);
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
