<script setup>
import { interviews } from '../data/interviews'
import { useSeo } from '../composables/useSeo'
import { homeSeo } from '../lib/seo'
import InterviewCard from '../components/InterviewCard.vue'
import ChatPanel from '../components/ChatPanel.vue'

const homeQuestions = [
  'What does a typical day look like for a NASA engineer?',
  'How did these engineers choose their majors?',
  'What advice do they have for students?',
]

const hosts = [
  {
    name: 'Joshua Babalola',
    role: 'Co-host',
    portfolio: '',
    email: '',
  },
  {
    name: 'David Cui',
    role: 'Co-host',
    portfolio: 'https://dczhportfolio.vercel.app/',
    email: 'davidcuizhh1@gmail.com',
  },
]

useSeo(homeSeo(interviews))
</script>

<template>
  <main>
    <!-- hero -->
    <section class="hero">
      <div class="container">
        <h1 class="rise r1">What engineers<br />actually do.</h1>
        <p class="hero-sub rise r2">
          Student-run interviews about the day-to-day life behind engineering
          careers — from NASA to Google to ISRO.
        </p>
        <div class="hero-cta rise r3">
          <a href="#interviews" class="btn btn-ink">Explore interviews</a>
          <a href="#ask" class="link-arrow">Ask the AI →</a>
        </div>
      </div>
    </section>

    <!-- interviews -->
    <section id="interviews" class="section">
      <div class="container">
        <div class="section-head" v-reveal>
          <h2>Interviews</h2>
        </div>
        <div class="cards-grid">
          <InterviewCard
            v-for="(p, i) in interviews"
            :key="p.id"
            :person="p"
            v-reveal="(i % 3) * 80"
          />
        </div>
      </div>
    </section>

    <!-- ask -->
    <section id="ask" class="section ask">
      <div class="container">
        <div class="section-head" v-reveal>
          <h2>Ask the AI</h2>
          <p>Answers come from the six interviews, with sources.</p>
        </div>
        <div class="ask-panel" v-reveal="100">
          <ChatPanel variant="panel" :suggestions="homeQuestions" />
        </div>
      </div>
    </section>

    <!-- hosts -->
    <section id="hosts" class="section hosts">
      <div class="container">
        <div class="section-head" v-reveal>
          <h2>The hosts</h2>
          <p>The students behind Beyond the Blueprint.</p>
        </div>
        <div class="hosts-grid">
          <div v-for="(h, i) in hosts" :key="h.name" class="host-card" v-reveal="i * 80">
            <strong>{{ h.name }}</strong>
            <span class="host-role">{{ h.role }}</span>
            <div v-if="h.portfolio || h.email" class="host-links">
              <a v-if="h.portfolio" :href="h.portfolio" target="_blank" rel="noopener">
                Portfolio ↗
              </a>
              <a v-if="h.email" :href="`mailto:${h.email}`">{{ h.email }}</a>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
/* hero */
.hero {
  padding: calc(var(--nav-h) + 108px) 0 40px;
}

.hero h1 {
  font-size: clamp(40px, 6.5vw, 64px);
  font-weight: 700;
  letter-spacing: -0.03em;
  line-height: 1.05;
}

.hero-sub {
  max-width: 460px;
  color: var(--muted);
  font-size: 17px;
  margin-top: 22px;
}

.hero-cta {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 34px;
  flex-wrap: wrap;
}

.rise {
  animation: rise 0.7s ease both;
}

.r1 { animation-delay: 0.05s; }
.r2 { animation-delay: 0.15s; }
.r3 { animation-delay: 0.25s; }

@keyframes rise {
  from { opacity: 0; transform: translateY(16px); }
  to { opacity: 1; transform: none; }
}

/* interviews */
.cards-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

@media (max-width: 960px) {
  .cards-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 620px) {
  .cards-grid {
    grid-template-columns: 1fr;
  }
}

/* ask */
.ask-panel {
  max-width: 680px;
}

/* hosts */
.hosts-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 320px));
  gap: 16px;
}

.host-card {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 22px 24px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: #fff;
}

.host-card strong {
  font-size: 16.5px;
  font-weight: 650;
}

.host-role {
  font-size: 13.5px;
  color: var(--faint);
}

.host-links {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-top: 12px;
  font-size: 14px;
}

.host-links a {
  color: var(--muted);
  width: fit-content;
  transition: color 0.2s ease;
}

.host-links a:hover {
  color: var(--accent);
}

@media (max-width: 620px) {
  .hosts-grid {
    grid-template-columns: 1fr;
  }
}

@media (prefers-reduced-motion: reduce) {
  .rise {
    animation: none;
  }
}
</style>
