import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../store/auth.js'
import Landing   from '../views/Landing.vue'
import Login     from '../views/Login.vue'
import Shortcuts from '../views/Shortcuts.vue'
import Admin     from '../views/Admin.vue'
import Ebooks    from '../views/Ebooks.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/',                   component: Landing,   meta: { public: true } },
    { path: '/login',              component: Login,     meta: { public: true } },
    { path: '/shortcuts',          component: Shortcuts },
    { path: '/shortcuts/:categoryId', component: Shortcuts },
    { path: '/admin',              component: Admin },
    { path: '/ebooks',             component: Ebooks },
  ],
})

router.beforeEach(async (to) => {
  if (to.meta.public) return true

  const auth = useAuthStore()
  // Only call the server once per session; after that trust the store
  if (!auth.checked) await auth.fetchMe()

  if (!auth.user) return { path: '/login', query: { next: to.fullPath } }
  return true
})

export default router
