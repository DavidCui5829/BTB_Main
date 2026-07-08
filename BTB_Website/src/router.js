import { createRouter, createWebHistory } from 'vue-router'
import HomePage from './pages/HomePage.vue'
import InterviewPage from './pages/InterviewPage.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomePage },
    { path: '/interviews/:id', name: 'interview', component: InterviewPage, props: true },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) return savedPosition
    if (to.hash) return { el: to.hash, top: 88, behavior: 'smooth' }
    return { top: 0 }
  },
})

export default router
