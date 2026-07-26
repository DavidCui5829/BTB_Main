// Light/dark theme, persisted and applied to <html data-theme>. The initial
// value is also set by an inline script in index.html (before first paint) to
// avoid a flash of the wrong theme; this composable keeps Vue in sync and lets
// the nav toggle it.
import { ref } from 'vue'

const STORAGE_KEY = 'btb-theme'

function initial() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved === 'light' || saved === 'dark') return saved
  } catch {
    /* ignore */
  }
  const prefersDark =
    typeof matchMedia === 'function' && matchMedia('(prefers-color-scheme: dark)').matches
  return prefersDark ? 'dark' : 'light'
}

// Module-level singleton so every component shares one reactive value.
const theme = ref(initial())

function apply(value) {
  theme.value = value
  document.documentElement.dataset.theme = value
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) meta.setAttribute('content', value === 'dark' ? '#0b0e14' : '#fcfcfb')
  try {
    localStorage.setItem(STORAGE_KEY, value)
  } catch {
    /* ignore */
  }
}

export function useTheme() {
  const toggleTheme = () => apply(theme.value === 'dark' ? 'light' : 'dark')
  return { theme, toggleTheme }
}
