<script setup>
import { onMounted } from 'vue'
import { interviews } from '../data/interviews'
import InterviewCard from '../components/InterviewCard.vue'
import ChatPanel from '../components/ChatPanel.vue'

const homeQuestions = [
  'What does a typical day look like for a NASA engineer?',
  'How did these engineers choose their majors?',
  'What advice do they have for students?',
]

onMounted(() => {
  document.title = 'Beyond the Blueprint'
})
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

@media (prefers-reduced-motion: reduce) {
  .rise {
    animation: none;
  }
}
</style>
