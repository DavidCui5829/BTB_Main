// v-reveal — fades an element up once it enters the viewport.
// Optional value is a stagger delay in milliseconds: v-reveal="120"
export const reveal = {
  mounted(el, binding) {
    el.classList.add('reveal')
    if (binding.value) el.style.transitionDelay = `${binding.value}ms`

    if (typeof IntersectionObserver === 'undefined') {
      el.classList.add('is-in')
      return
    }

    const io = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            el.classList.add('is-in')
            io.disconnect()
          }
        }
      },
      { threshold: 0.12, rootMargin: '0px 0px -40px 0px' }
    )
    io.observe(el)
    el._revealObserver = io
  },
  unmounted(el) {
    el._revealObserver?.disconnect()
  },
}
