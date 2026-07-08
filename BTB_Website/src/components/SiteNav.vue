<script setup>
import { onMounted, onUnmounted, ref } from 'vue'

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
  transition: background 0.25s ease, border-color 0.25s ease;
}

.nav--scrolled {
  background: rgba(252, 252, 251, 0.85);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom-color: var(--border);
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
  font-size: 14.5px;
  font-weight: 500;
  color: var(--muted);
  transition: color 0.2s ease;
}

.nav-links a:hover {
  color: var(--text);
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
