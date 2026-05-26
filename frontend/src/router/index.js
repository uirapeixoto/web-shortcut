import { createRouter, createWebHistory } from 'vue-router'
import Landing from '../views/Landing.vue'
import Shortcuts from '../views/Shortcuts.vue'
import Admin from '../views/Admin.vue'
import Ebooks from '../views/Ebooks.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Landing },
    { path: '/shortcuts', component: Shortcuts },
    { path: '/shortcuts/:categoryId', component: Shortcuts },
    { path: '/admin', component: Admin },
    { path: '/ebooks', component: Ebooks },
  ]
})
