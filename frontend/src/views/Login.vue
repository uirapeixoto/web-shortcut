<template>
  <div class="login-page">
    <!-- Animated background blobs -->
    <div class="bg-blob blob-1"></div>
    <div class="bg-blob blob-2"></div>
    <div class="bg-blob blob-3"></div>

    <div class="login-card">

      <!-- Logo -->
      <div class="login-logo">
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round">
          <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/>
        </svg>
      </div>

      <h1 class="login-app">WebShortcut</h1>
      <p class="login-sub">Acesso restrito — faça login para continuar</p>

      <!-- Avatar / user hint -->
      <div class="login-avatar">
        <span>UP</span>
      </div>

      <form class="login-form" @submit.prevent="submit" novalidate>

        <div class="field-group" :class="{ 'field-group--error': errors.email }">
          <label for="email">E-mail</label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            <input
              id="email"
              v-model="email"
              type="email"
              autocomplete="email"
              placeholder="seu@email.com"
              :disabled="loading"
              @input="errors.email = ''"
            />
          </div>
          <span class="field-err" v-if="errors.email">{{ errors.email }}</span>
        </div>

        <div class="field-group" :class="{ 'field-group--error': errors.password }">
          <label for="password">Senha</label>
          <div class="field-wrap">
            <svg class="field-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            <input
              id="password"
              v-model="password"
              :type="showPwd ? 'text' : 'password'"
              autocomplete="current-password"
              placeholder="••••••••"
              :disabled="loading"
              @input="errors.password = ''"
            />
            <button type="button" class="pwd-toggle" @click="showPwd = !showPwd" tabindex="-1">
              <svg v-if="!showPwd" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
              <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
            </button>
          </div>
          <span class="field-err" v-if="errors.password">{{ errors.password }}</span>
        </div>

        <!-- Global error -->
        <Transition name="err-fade">
          <div class="login-error" v-if="globalError">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            {{ globalError }}
          </div>
        </Transition>

        <button type="submit" class="login-btn" :disabled="loading">
          <span v-if="!loading">Entrar</span>
          <span v-else class="login-spinner"></span>
        </button>

      </form>

      <p class="login-footer">WebShortcut Manager · Uso pessoal</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../store/auth.js'

const router = useRouter()
const route  = useRoute()
const auth   = useAuthStore()

const email       = ref('')
const password    = ref('')
const showPwd     = ref(false)
const loading     = ref(false)
const globalError = ref('')
const errors      = ref({ email: '', password: '' })

async function submit() {
  globalError.value = ''
  errors.value = { email: '', password: '' }

  if (!email.value.trim()) { errors.value.email = 'Informe o e-mail'; return }
  if (!password.value)     { errors.value.password = 'Informe a senha'; return }

  loading.value = true
  try {
    await auth.login(email.value.trim(), password.value)
    const next = typeof route.query.next === 'string' ? route.query.next : '/shortcuts'
    router.replace(next)
  } catch (e) {
    globalError.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
/* ── Page ────────────────────────────────────────── */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #060912;
  position: relative;
  overflow: hidden;
  padding: 24px;
}

/* ── Animated background blobs ───────────────────── */
.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.18;
  animation: float 8s ease-in-out infinite alternate;
}
.blob-1 { width: 420px; height: 420px; background: #6366f1; top: -100px; left: -80px; animation-delay: 0s; }
.blob-2 { width: 300px; height: 300px; background: #8b5cf6; bottom: -60px; right: -60px; animation-delay: -3s; }
.blob-3 { width: 200px; height: 200px; background: #3b82f6; top: 40%; left: 60%; animation-delay: -6s; }
@keyframes float {
  from { transform: translate(0, 0) scale(1);   }
  to   { transform: translate(20px, 30px) scale(1.05); }
}

/* ── Card ────────────────────────────────────────── */
.login-card {
  position: relative;
  z-index: 1;
  width: min(400px, 100%);
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 20px;
  padding: 40px 36px 32px;
  backdrop-filter: blur(24px);
  box-shadow: 0 40px 80px rgba(0,0,0,0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

/* ── Logo / App name ─────────────────────────────── */
.login-logo {
  width: 56px; height: 56px;
  border-radius: 16px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  display: flex; align-items: center; justify-content: center;
  color: #fff;
  margin-bottom: 4px;
  box-shadow: 0 8px 24px rgba(99,102,241,0.4);
}
.login-app {
  font-size: 1.3rem; font-weight: 800; color: #f1f5f9; margin: 0;
  letter-spacing: -0.02em;
}
.login-sub {
  font-size: 0.78rem; color: #64748b; margin: 0 0 10px; text-align: center;
}

/* ── Avatar ──────────────────────────────────────── */
.login-avatar {
  width: 52px; height: 52px; border-radius: 50%;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  display: flex; align-items: center; justify-content: center;
  font-size: 1rem; font-weight: 700; color: #fff;
  margin: 8px 0 16px;
  box-shadow: 0 0 0 3px rgba(99,102,241,0.25);
}

/* ── Form ────────────────────────────────────────── */
.login-form { width: 100%; display: flex; flex-direction: column; gap: 14px; }

.field-group { display: flex; flex-direction: column; gap: 5px; }
.field-group label {
  font-size: 0.72rem; font-weight: 600;
  text-transform: uppercase; letter-spacing: 0.06em; color: #64748b;
}

.field-wrap {
  position: relative; display: flex; align-items: center;
}
.field-icon {
  position: absolute; left: 12px; color: #475569; pointer-events: none;
  flex-shrink: 0;
}
.field-wrap input {
  width: 100%;
  padding: 11px 40px 11px 38px;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 10px;
  color: #e2e8f0; font-size: 0.88rem;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
}
.field-wrap input:focus {
  outline: none;
  border-color: rgba(99,102,241,0.6);
  box-shadow: 0 0 0 3px rgba(99,102,241,0.12);
}
.field-wrap input:disabled { opacity: 0.5; cursor: not-allowed; }
.field-wrap input::placeholder { color: #334155; }

.field-group--error .field-wrap input { border-color: rgba(239,68,68,0.5); }
.field-err { font-size: 0.72rem; color: #f87171; margin-top: 2px; }

.pwd-toggle {
  position: absolute; right: 10px;
  background: none; border: none; color: #475569;
  cursor: pointer; padding: 4px;
  transition: color 0.15s;
}
.pwd-toggle:hover { color: #94a3b8; }

/* ── Global error ────────────────────────────────── */
.login-error {
  display: flex; align-items: center; gap: 7px;
  padding: 10px 12px;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.25);
  border-radius: 8px;
  font-size: 0.8rem; color: #f87171;
}
.err-fade-enter-active, .err-fade-leave-active { transition: opacity 0.25s; }
.err-fade-enter-from, .err-fade-leave-to { opacity: 0; }

/* ── Submit ──────────────────────────────────────── */
.login-btn {
  width: 100%; padding: 13px;
  border-radius: 10px; border: none;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff; font-size: 0.92rem; font-weight: 700;
  cursor: pointer; letter-spacing: 0.02em;
  transition: opacity 0.15s, transform 0.1s;
  display: flex; align-items: center; justify-content: center;
  min-height: 46px;
  margin-top: 4px;
  box-shadow: 0 4px 16px rgba(99,102,241,0.35);
}
.login-btn:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
.login-btn:active:not(:disabled) { transform: translateY(0); }
.login-btn:disabled { opacity: 0.55; cursor: not-allowed; }

.login-spinner {
  width: 18px; height: 18px;
  border: 2px solid rgba(255,255,255,0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Footer ──────────────────────────────────────── */
.login-footer {
  font-size: 0.7rem; color: #1e293b;
  margin-top: 16px; text-align: center;
}
</style>
