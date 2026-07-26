<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useTheme } from '../composables/useTheme'

const { theme, toggleTheme } = useTheme()
const scrolled = ref(false)
const onScroll = () => (scrolled.value = window.scrollY > 8)

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onUnmounted(() => window.removeEventListener('scroll', onScroll))
</script>

<template>
  <header class="nav" :class="{ 'nav--scrolled': scrolled }">
    <div class="container nav-inner">
      <router-link to="/" class="brand" aria-label="Beyond the Blueprint — home">
        <img src="/btb-cover.png" class="brand-mark" alt="" />
        <span class="brand-name">Beyond the Blueprint</span>
      </router-link>

      <nav class="nav-links" aria-label="Main">
        <router-link :to="{ path: '/', hash: '#interviews' }">Interviews</router-link>
        <router-link :to="{ path: '/', hash: '#ask' }">Ask AI</router-link>
      </nav>

      <button
        class="theme-toggle"
        type="button"
        @click="toggleTheme"
        :aria-label="theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'"
        :title="theme === 'dark' ? 'Light mode' : 'Dark mode'"
      >
        <svg
          v-if="theme !== 'dark'"
          viewBox="0 0 24 24"
          width="18"
          height="18"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
        </svg>
        <svg
          v-else
          viewBox="0 0 24 24"
          width="18"
          height="18"
          fill="none"
          stroke="currentColor"
          stroke-width="1.8"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="4" />
          <path
            d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M4.93 19.07l1.41-1.41M17.66 6.34l1.41-1.41"
          />
        </svg>
      </button>
    </div>
  </header>
</template>

<style scoped>
.nav {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 50;
  height: var(--nav-h);
  display: flex;
  align-items: center;
  border-bottom: 1px solid transparent;
  transition: background 0.25s ease, border-color 0.25s ease, height 0.25s ease,
    box-shadow 0.25s ease;
}

.nav--scrolled {
  height: 54px;
  background: var(--nav-bg);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom-color: var(--border);
  box-shadow: 0 4px 24px rgba(15, 17, 20, 0.05);
}

.nav-inner {
  display: flex;
  align-items: center;
  gap: 28px;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  margin-right: auto;
}

.brand-mark {
  width: 28px;
  height: 28px;
  border-radius: 7px;
  object-fit: cover;
}

.brand-name {
  font-weight: 650;
  font-size: 15.5px;
  letter-spacing: -0.01em;
}

.nav-links {
  display: flex;
  gap: 24px;
}

.nav-links a {
  position: relative;
  font-size: 14.5px;
  font-weight: 500;
  color: var(--muted);
  transition: color 0.2s ease;
}

.nav-links a::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: -5px;
  width: 100%;
  height: 1.5px;
  border-radius: 2px;
  background: var(--accent);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.25s ease;
}

.nav-links a:hover {
  color: var(--text);
}

.nav-links a:hover::after {
  transform: scaleX(1);
}

.theme-toggle {
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  margin-left: 4px;
  border-radius: 9px;
  color: var(--muted);
  transition: color 0.2s ease, background 0.2s ease;
}

.theme-toggle:hover {
  color: var(--text);
  background: var(--surface);
}

@media (max-width: 560px) {
  .brand-name {
    font-size: 14.5px;
  }
  .nav-links {
    gap: 18px;
  }
}
</style>
