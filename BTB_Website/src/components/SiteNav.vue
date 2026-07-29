<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useTheme } from '../composables/useTheme'
import { useI18n } from '../composables/useI18n'

const { theme, toggleTheme } = useTheme()
const { t, locale, locales, setLocale } = useI18n()
const scrolled = ref(false)
const onScroll = () => (scrolled.value = window.scrollY > 8)

// Custom language dropdown — a native <select> popup is OS-rendered and can't be
// themed for dark mode, so we render our own menu styled with the theme vars.
const langEl = ref(null)
const langOpen = ref(false)
function pickLang(code) {
  setLocale(code)
  langOpen.value = false
}
function onDocPointer(e) {
  if (langOpen.value && langEl.value && !langEl.value.contains(e.target)) {
    langOpen.value = false
  }
}
function onKeydown(e) {
  if (e.key === 'Escape') langOpen.value = false
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
  document.addEventListener('click', onDocPointer)
  document.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('scroll', onScroll)
  document.removeEventListener('click', onDocPointer)
  document.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <header class="nav" :class="{ 'nav--scrolled': scrolled }">
    <div class="container nav-inner">
      <router-link to="/" class="brand" :aria-label="t('nav.homeAria')">
        <img src="/btb-cover.png" class="brand-mark" alt="" />
        <span class="brand-name">Beyond the Blueprint</span>
      </router-link>

      <nav class="nav-links" :aria-label="t('nav.mainAria')">
        <router-link :to="{ path: '/', hash: '#interviews' }">{{ t('nav.interviews') }}</router-link>
        <router-link :to="{ path: '/', hash: '#ask' }">{{ t('nav.askAi') }}</router-link>
        <router-link :to="{ path: '/', hash: '#about' }">{{ t('nav.about') }}</router-link>
      </nav>

      <div class="lang" ref="langEl">
        <button
          class="lang-btn"
          type="button"
          :aria-label="t('nav.language')"
          :title="t('nav.language')"
          :aria-expanded="langOpen"
          aria-haspopup="listbox"
          @click="langOpen = !langOpen"
        >
          <svg
            viewBox="0 0 24 24"
            width="18"
            height="18"
            fill="none"
            stroke="currentColor"
            stroke-width="1.7"
            stroke-linecap="round"
            stroke-linejoin="round"
            aria-hidden="true"
          >
            <circle cx="12" cy="12" r="9" />
            <path d="M3 12h18M12 3a14 14 0 0 1 0 18M12 3a14 14 0 0 0 0 18" />
          </svg>
        </button>
        <ul v-if="langOpen" class="lang-menu" role="listbox" :aria-label="t('nav.language')">
          <li v-for="l in locales" :key="l.code">
            <button
              type="button"
              class="lang-option"
              :class="{ 'is-active': l.code === locale }"
              role="option"
              :aria-selected="l.code === locale"
              @click="pickLang(l.code)"
            >
              {{ l.label }}
            </button>
          </li>
        </ul>
      </div>

      <button
        class="theme-toggle"
        type="button"
        @click="toggleTheme"
        :aria-label="theme === 'dark' ? t('nav.switchToLight') : t('nav.switchToDark')"
        :title="theme === 'dark' ? t('nav.lightMode') : t('nav.darkMode')"
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
  border-radius: 9px;
  color: var(--muted);
  transition: color 0.2s ease, background 0.2s ease;
}

.theme-toggle:hover {
  color: var(--text);
  background: var(--surface);
}

/* Language switcher: a globe button (same 36px footprint as the theme toggle)
   that opens a custom menu. Custom rather than a native <select> because the
   native popup is OS-rendered and can't be themed for dark mode. */
.lang {
  position: relative;
  display: inline-grid;
  place-items: center;
}

.lang-btn {
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 9px;
  color: var(--muted);
  transition: color 0.2s ease, background 0.2s ease;
}

.lang-btn:hover {
  color: var(--text);
  background: var(--surface);
}

.lang-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 60;
  min-width: 128px;
  list-style: none;
  padding: 6px;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--card);
  box-shadow: 0 12px 32px rgba(15, 17, 20, 0.14);
  animation: lang-in 0.16s ease both;
}

:root[data-theme='dark'] .lang-menu {
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.55);
}

@keyframes lang-in {
  from { opacity: 0; transform: translateY(-4px); }
  to { opacity: 1; transform: none; }
}

.lang-option {
  display: flex;
  width: 100%;
  align-items: center;
  padding: 9px 12px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--muted);
  text-align: left;
  transition: color 0.15s ease, background 0.15s ease;
}

.lang-option:hover {
  color: var(--text);
  background: var(--surface);
}

.lang-option.is-active {
  color: var(--accent);
  font-weight: 600;
}

@media (prefers-reduced-motion: reduce) {
  .lang-menu {
    animation: none;
  }
}

@media (max-width: 560px) {
  .nav-inner {
    gap: 10px;
  }
  /* logo-only on phones — the full wordmark + links + controls won't fit */
  .brand-name {
    display: none;
  }
  .nav-links {
    gap: 16px;
  }
  .nav-links a {
    font-size: 14px;
  }
}

@media (max-width: 380px) {
  .nav-inner {
    gap: 8px;
  }
  .nav-links {
    gap: 13px;
  }
  .nav-links a {
    font-size: 13px;
  }
  .lang-btn,
  .theme-toggle {
    width: 32px;
    height: 32px;
  }
}
</style>
