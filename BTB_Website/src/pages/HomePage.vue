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

function initials(name) {
  return name
    .split(/\s+/)
    .map((w) => w[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

useSeo(homeSeo(interviews))
</script>

<template>
  <main>
    <!-- hero -->
    <section class="hero">
      <div class="hero-aura" aria-hidden="true">
        <span class="blob b1"></span>
        <span class="blob b2"></span>
        <span class="blob b3"></span>
      </div>
      <div class="container hero-inner">
        <div class="hero-content">
          <p class="hero-eyebrow rise r1">Student-run engineering interviews</p>
          <h1 class="rise r2">What engineers<br /><span class="grad">actually do.</span></h1>
          <p class="hero-sub rise r3">
            The day-to-day life behind engineering careers — real people, real work,
            from NASA to Google to ISRO. Watch the interviews, or just ask.
          </p>
          <div class="hero-cta rise r4">
            <a href="#interviews" class="btn btn-ink">Explore interviews</a>
          </div>
        </div>
        <div id="ask" class="hero-chat rise r3">
          <ChatPanel variant="panel" :suggestions="homeQuestions" />
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

    <!-- hosts -->
    <section id="hosts" class="section hosts">
      <div class="container">
        <div class="section-head" v-reveal>
          <h2>The hosts</h2>
          <p>The students behind Beyond the Blueprint.</p>
        </div>
        <div class="hosts-grid">
          <div v-for="(h, i) in hosts" :key="h.name" class="host-card" v-reveal="i * 80">
            <span class="avatar" aria-hidden="true">{{ initials(h.name) }}</span>
            <div class="host-info">
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
      </div>
    </section>
  </main>
</template>

<style scoped>
/* hero */
.hero {
  position: relative;
  overflow: hidden;
  padding: calc(var(--nav-h) + 66px) 0 82px;
}

.hero-inner {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: minmax(0, 1fr) 400px;
  gap: 50px;
  align-items: center;
}

.hero-content {
  min-width: 0;
}

.hero-chat {
  min-width: 0;
}

@media (max-width: 1080px) {
  .hero {
    padding: calc(var(--nav-h) + 72px) 0 56px;
  }
  .hero-inner {
    grid-template-columns: 1fr;
    gap: 36px;
  }
  /* keep the AI chat visible on smaller screens — it's the headline feature */
  .hero-chat {
    max-width: 560px;
  }
}

.hero-eyebrow {
  display: inline-block;
  font-size: 12.5px;
  font-weight: 600;
  letter-spacing: 0.09em;
  text-transform: uppercase;
  color: var(--accent);
  margin-bottom: 18px;
}

.hero h1 {
  font-size: clamp(44px, 7.2vw, 74px);
  font-weight: 700;
  letter-spacing: -0.035em;
  line-height: 1.02;
}

.grad {
  background: linear-gradient(100deg, var(--accent), #6a5cff 52%, #17b6d6);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.hero-sub {
  max-width: 480px;
  color: var(--muted);
  font-size: 17.5px;
  margin-top: 24px;
}

/* animated aurora backdrop */
.hero-aura {
  position: absolute;
  inset: -25% -10% auto -10%;
  height: 150%;
  z-index: 0;
  pointer-events: none;
  filter: blur(70px);
  opacity: 0.42;
}

:root[data-theme='dark'] .hero-aura {
  opacity: 0.58;
}

.blob {
  position: absolute;
  width: 44vw;
  max-width: 580px;
  aspect-ratio: 1;
  border-radius: 50%;
  will-change: transform;
}

.b1 {
  left: -6%;
  top: -8%;
  background: radial-gradient(circle, #2f5cff, transparent 68%);
  animation: drift1 19s ease-in-out infinite;
}

.b2 {
  right: -4%;
  top: 2%;
  background: radial-gradient(circle, #8b5cf6, transparent 68%);
  animation: drift2 23s ease-in-out infinite;
}

.b3 {
  left: 26%;
  top: 22%;
  background: radial-gradient(circle, #06b6d4, transparent 70%);
  animation: drift3 27s ease-in-out infinite;
}

@keyframes drift1 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(6%, 8%); }
}
@keyframes drift2 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(-7%, 6%); }
}
@keyframes drift3 {
  0%, 100% { transform: translate(0, 0); }
  50% { transform: translate(5%, -6%); }
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
.r4 { animation-delay: 0.35s; }

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
  flex-direction: row;
  align-items: flex-start;
  gap: 16px;
  padding: 22px 24px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--card);
}

.avatar {
  flex: none;
  width: 46px;
  height: 46px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 15px;
  font-weight: 650;
  color: #fff;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, var(--accent), #16307a);
}

.host-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
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
  .blob {
    animation: none;
  }
}
</style>
