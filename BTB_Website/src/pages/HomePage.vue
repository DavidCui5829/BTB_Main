<script setup>
import { computed, ref } from 'vue'
import { interviews } from '../data/interviews'
import { useSeo } from '../composables/useSeo'
import { useI18n } from '../composables/useI18n'
import { homeSeo } from '../lib/seo'
import InterviewCard from '../components/InterviewCard.vue'
import FeaturedEpisode from '../components/FeaturedEpisode.vue'
import ChatPanel from '../components/ChatPanel.vue'

const { t } = useI18n()

// Latest episode, spotlighted below the hero (still appears in the grid too).
const featured = [...interviews].sort((a, b) => (b.episode || 0) - (a.episode || 0))[0]

// Re-derives on locale change (t reads the reactive locale).
const homeQuestions = computed(() => [t('home.q1'), t('home.q2'), t('home.q3')])

// David first — he designed and built the site and the AI. Role/note are i18n
// keys (resolved at render) since they're interface copy, not interview data.
const team = [
  {
    name: 'David Cui',
    roleKey: 'home.team.builderRole',
    noteKey: 'home.team.davidNote',
    portfolio: 'https://dczhportfolio.vercel.app/',
    email: 'davidcuizhh1@gmail.com',
    photo: '/hosts/david-cui.jpg',
  },
  {
    name: 'Joshua Babalola',
    roleKey: 'home.team.coHost',
    noteKey: '',
    portfolio: '',
    email: '',
  },
]

// Fall back to the monogram avatar if a host photo is missing.
const brokenPhoto = ref({})
function onPhotoError(name) {
  brokenPhoto.value = { ...brokenPhoto.value, [name]: true }
}

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
          <p class="hero-eyebrow rise r1">{{ t('home.eyebrow') }}</p>
          <h1 class="rise r2">{{ t('home.titleLine1') }}<br /><span class="grad">{{ t('home.titleLine2') }}</span></h1>
          <p class="hero-sub rise r3">{{ t('home.sub') }}</p>
          <div class="hero-cta rise r4">
            <a href="#interviews" class="btn btn-ink">{{ t('home.cta') }}</a>
          </div>
        </div>
        <div id="ask" class="hero-chat rise r3">
          <ChatPanel variant="panel" :suggestions="homeQuestions" />
        </div>
      </div>
    </section>

    <!-- latest + interviews -->
    <section id="interviews" class="section">
      <div class="container">
        <div class="home-featured" v-reveal>
          <FeaturedEpisode :person="featured" />
        </div>
        <div class="section-head" v-reveal>
          <h2>{{ t('home.allInterviews') }}</h2>
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

    <!-- about / story -->
    <section id="about" class="section about">
      <div class="container">
        <div class="section-head" v-reveal>
          <h2>{{ t('home.about.heading') }}</h2>
        </div>

        <div class="about-story" v-reveal>
          <p class="lead" v-html="t('home.about.lead')"></p>
          <p>{{ t('home.about.p1') }}</p>
          <p>{{ t('home.about.p2') }}</p>
        </div>

        <h3 class="team-heading" v-reveal>{{ t('home.about.teamHeading') }}</h3>
        <div class="team" v-reveal="80">
          <article v-for="h in team" :key="h.name" class="team-card">
            <img
              v-if="h.photo && !brokenPhoto[h.name]"
              class="team-avatar"
              :src="h.photo"
              :alt="h.name"
              loading="lazy"
              @error="onPhotoError(h.name)"
            />
            <span v-else class="team-avatar team-monogram" aria-hidden="true">{{ initials(h.name) }}</span>
            <div class="team-info">
              <strong>{{ h.name }}</strong>
              <span class="team-role">{{ t(h.roleKey) }}</span>
              <p v-if="h.noteKey" class="team-note">{{ t(h.noteKey) }}</p>
              <div v-if="h.portfolio || h.email" class="team-links">
                <a v-if="h.portfolio" :href="h.portfolio" target="_blank" rel="noopener">{{ t('home.team.portfolio') }}</a>
                <a v-if="h.email" :href="`mailto:${h.email}`">{{ t('home.team.email') }}</a>
              </div>
            </div>
          </article>
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

@media (max-width: 560px) {
  .hero {
    padding: calc(var(--nav-h) + 34px) 0 44px;
  }
  .hero-sub {
    font-size: 16px;
  }
  /* full-width, thumb-friendly CTA on phones */
  .hero-cta .btn {
    width: 100%;
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
.home-featured {
  margin-bottom: 44px;
}

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

/* about / story */
.about-story {
  max-width: 680px;
  margin-bottom: 48px;
}

.about-story .lead {
  font-size: 20px;
  line-height: 1.5;
  font-weight: 550;
  letter-spacing: -0.01em;
  color: var(--text);
  margin-bottom: 18px;
}

.about-story .lead em {
  font-style: italic;
}

.about-story p:not(.lead) {
  color: var(--muted);
  font-size: 16px;
  line-height: 1.75;
  margin-bottom: 14px;
  max-width: 640px;
}

.team-heading {
  font-size: 14px;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  color: var(--faint);
  margin-bottom: 18px;
}

.team {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 400px));
  gap: 18px;
}

.team-card {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
  padding: 24px;
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--card);
}

.team-avatar {
  flex: none;
  width: 140px;
  height: 140px;
  border-radius: 16px;
  object-fit: cover;
  object-position: center;
  background: var(--surface);
}

.team-monogram {
  display: grid;
  place-items: center;
  font-size: 46px;
  font-weight: 650;
  color: #fff;
  letter-spacing: 0.02em;
  background: linear-gradient(135deg, var(--accent), #16307a);
}

.team-info {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.team-info strong {
  font-size: 17px;
  font-weight: 650;
}

.team-role {
  font-size: 13.5px;
  font-weight: 550;
  color: var(--accent);
}

.team-note {
  margin-top: 7px;
  font-size: 13.5px;
  line-height: 1.55;
  color: var(--muted);
}

.team-links {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  font-size: 13.5px;
}

.team-links a {
  color: var(--muted);
  transition: color 0.2s ease;
}

.team-links a:hover {
  color: var(--accent);
}

@media (max-width: 720px) {
  .team {
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
