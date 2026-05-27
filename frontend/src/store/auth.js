import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const user    = ref(null)   // { name, email } or null
  const checked = ref(false)  // true after first fetchMe completes

  async function fetchMe() {
    try {
      const r = await fetch('/api/auth/me')
      user.value = r.ok ? await r.json() : null
    } catch {
      user.value = null
    } finally {
      checked.value = true
    }
  }

  async function login(email, password) {
    const r = await fetch('/api/auth/login', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email, password }),
    })
    if (!r.ok) {
      const body = await r.json().catch(() => ({}))
      throw new Error(body.detail || 'Erro ao fazer login')
    }
    user.value = await r.json()
    checked.value = true
  }

  async function logout() {
    await fetch('/api/auth/logout', { method: 'POST' }).catch(() => {})
    user.value    = null
    checked.value = false
  }

  return { user, checked, fetchMe, login, logout }
})
