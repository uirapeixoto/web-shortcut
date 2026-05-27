<template>
  <header class="top-menu">
    <div class="top-left">
      <button class="toggle-btn" @click="store.sideOpen = !store.sideOpen" title="Menu">
        <span class="hamburger">☰</span>
      </button>
      <router-link to="/shortcuts" class="brand">🚀 WebShortcut</router-link>
    </div>

    <nav class="top-nav">
      <router-link to="/shortcuts">Atalhos</router-link>
      <router-link to="/admin">⚙ Gerenciar</router-link>
    </nav>

    <div class="top-user" v-if="auth.user">
      <div class="user-avatar" :title="auth.user.name">
        {{ initials }}
      </div>
      <span class="user-name">{{ firstName }}</span>
      <button class="logout-btn" @click="doLogout" title="Sair">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
      </button>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from '../store/index.js'
import { useAuthStore } from '../store/auth.js'

const store  = useStore()
const auth   = useAuthStore()
const router = useRouter()

const initials  = computed(() => {
  if (!auth.user?.name) return '?'
  return auth.user.name.split(' ').slice(0, 2).map(w => w[0]).join('').toUpperCase()
})
const firstName = computed(() => auth.user?.name?.split(' ')[0] ?? '')

async function doLogout() {
  await auth.logout()
  router.push('/login')
}
</script>

<style scoped>
.top-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.user-avatar {
  width: 30px; height: 30px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.65rem; font-weight: 700; color: #fff;
  cursor: default; flex-shrink: 0;
}

.user-name {
  font-size: 0.8rem;
  color: var(--text-muted, #94a3b8);
  font-weight: 500;
  white-space: nowrap;
}

.logout-btn {
  background: none;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  color: #64748b;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.logout-btn:hover { background: rgba(239,68,68,0.1); color: #f87171; }
</style>
