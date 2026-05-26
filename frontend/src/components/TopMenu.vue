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
  </header>
</template>

<script setup>
import { useStore } from '../store/index.js'
const store = useStore()
</script>
