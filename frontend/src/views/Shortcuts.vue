<template>
  <div class="shortcuts-page">
    <div class="page-header">
      <h2>{{ currentCategory ? currentCategory.icon + ' ' + currentCategory.name : '🏠 Todos os Atalhos' }}</h2>
      <span class="count">{{ store.shortcuts.length }} atalho(s)</span>
    </div>

    <div v-if="store.shortcuts.length === 0" class="empty-state">
      <div class="empty-icon">🔍</div>
      <p>Nenhum atalho aqui ainda.</p>
      <router-link to="/admin" class="btn-sm">+ Adicionar</router-link>
    </div>

    <div class="shortcuts-grid" v-else>
      <ShortcutCard v-for="s in store.shortcuts" :key="s.id" :shortcut="s" />
    </div>
  </div>
</template>

<script setup>
import { watch, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useStore } from '../store/index.js'
import ShortcutCard from '../components/ShortcutCard.vue'

const route = useRoute()
const store = useStore()

const currentCategory = computed(() =>
  route.params.categoryId ? store.categories.find(c => c.id == route.params.categoryId) : null
)

async function load() {
  await store.fetchShortcuts(route.params.categoryId || null)
}

onMounted(load)
watch(() => route.params.categoryId, load)
</script>
