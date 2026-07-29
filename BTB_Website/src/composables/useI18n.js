// Site language, persisted to localStorage and applied to <html lang>. Mirrors
// the useTheme composable: a module-level singleton ref so every component
// shares one reactive locale, and t() re-renders wherever it's used the moment
// the locale changes.
//
// Deliberately dependency-free (no vue-i18n): the site's UI copy is small and a
// dot-path lookup with an English fallback covers everything we need.
import { ref, watch } from 'vue'
import { messages, LOCALES } from '../i18n/messages'
import { interviewContent } from '../i18n/interview-content'

const STORAGE_KEY = 'btb-locale'
const SUPPORTED = LOCALES.map((l) => l.code)
const DEFAULT = 'en'

function initial() {
  try {
    const saved = localStorage.getItem(STORAGE_KEY)
    if (saved && SUPPORTED.includes(saved)) return saved
  } catch {
    /* ignore */
  }
  // Fall back to the browser's preferred language (e.g. 'fr-CA' → 'fr').
  const nav = typeof navigator !== 'undefined' ? navigator.language || '' : ''
  const base = nav.toLowerCase().split('-')[0]
  if (SUPPORTED.includes(base)) return base
  return DEFAULT
}

// Module-level singleton — one shared reactive value for the whole app.
const locale = ref(initial())

// Walk a dot-path ('home.about.lead') into a messages object; undefined if any
// segment is missing.
function lookup(dict, path) {
  return path.split('.').reduce((obj, key) => (obj == null ? obj : obj[key]), dict)
}

// Translate a key for the current locale, falling back to English, then to the
// raw key so a typo is visible rather than silently blank. `params` fills
// {placeholders}.
function t(key, params) {
  let str = lookup(messages[locale.value], key)
  if (str == null) str = lookup(messages[DEFAULT], key)
  if (str == null) return key
  if (params) {
    str = str.replace(/\{(\w+)\}/g, (m, name) =>
      params[name] == null ? m : String(params[name])
    )
  }
  return str
}

// Translate a per-interview content field (field / role / intro / highlights /
// quote) for the current locale, falling back to the English value already on
// the interview object. `person` is an entry from data/interviews.json; `field`
// is one of its keys. Reads locale.value so callers re-render on switch.
function tc(person, field) {
  if (!person) return ''
  const fallback = person[field]
  if (locale.value === DEFAULT) return fallback
  const overlay = interviewContent[locale.value]?.[person.id]
  const value = overlay ? overlay[field] : undefined
  return value == null ? fallback : value
}

function apply(value) {
  const next = SUPPORTED.includes(value) ? value : DEFAULT
  locale.value = next
  if (typeof document !== 'undefined') document.documentElement.lang = next
  try {
    localStorage.setItem(STORAGE_KEY, next)
  } catch {
    /* ignore */
  }
}

// Keep <html lang> and storage in sync however the ref is changed (v-model on
// the switcher writes it directly).
watch(locale, apply, { immediate: true })

export function useI18n() {
  return { locale, setLocale: apply, t, tc, locales: LOCALES }
}
