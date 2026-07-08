<script setup>
defineProps({
  person: { type: Object, required: true },
})
</script>

<template>
  <router-link :to="`/interviews/${person.id}`" class="card">
    <div class="card-meta meta">
      <span>EP {{ String(person.episode).padStart(2, '0') }}</span>
      <span>{{ person.field }}</span>
    </div>
    <h3>{{ person.name }}</h3>
    <p>{{ person.role }} · {{ person.org }}</p>
    <svg class="arrow" viewBox="0 0 24 24" width="16" height="16" fill="none" aria-hidden="true">
      <path
        d="M5 12h14m0 0-6-6m6 6-6 6"
        stroke="currentColor"
        stroke-width="1.8"
        stroke-linecap="round"
        stroke-linejoin="round"
      />
    </svg>
  </router-link>
</template>

<style scoped>
.card {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 24px;
  border-radius: var(--radius-lg);
  border: 1px solid var(--border);
  background: #fff;
  transition: border-color 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}

.card:hover {
  border-color: var(--border-strong);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(20, 22, 26, 0.06);
}

.card-meta {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

h3 {
  font-size: 17.5px;
  font-weight: 650;
}

p {
  color: var(--muted);
  font-size: 14px;
}

.arrow {
  position: absolute;
  right: 22px;
  bottom: 22px;
  color: var(--faint);
  opacity: 0;
  transform: translateX(-6px);
  transition: opacity 0.25s ease, transform 0.25s ease, color 0.25s ease;
}

.card:hover .arrow {
  opacity: 1;
  transform: none;
  color: var(--accent);
}
</style>
