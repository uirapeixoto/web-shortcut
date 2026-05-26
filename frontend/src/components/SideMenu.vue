<template>
  <aside class="side-menu" :class="{ closed: !store.sideOpen }">
    <div class="side-header">
      <span v-if="store.sideOpen">Categorias</span>
    </div>
    <ul>
      <li>
        <router-link to="/shortcuts" class="side-item" @click="maybeClose">
          <span class="side-icon">🏠</span>
          <span class="side-label" v-if="store.sideOpen">Todos</span>
        </router-link>
      </li>
      <li v-for="cat in store.categories" :key="cat.id">
        <router-link :to="`/shortcuts/${cat.id}`" class="side-item" @click="maybeClose">
          <span class="side-icon">{{ cat.icon }}</span>
          <span class="side-label" v-if="store.sideOpen">{{ cat.name }}</span>
          <span class="cat-dot" :style="{ background: cat.color }" v-if="store.sideOpen"></span>
        </router-link>
      </li>
    </ul>

    <div class="side-bottom">
      <button
        class="side-item md-open-btn"
        :class="{ active: kanbanOpen }"
        @click="kanbanOpen = !kanbanOpen"
        :title="store.sideOpen ? 'Ctrl+K' : 'Kanban (Ctrl+K)'"
      >
        <span class="side-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="3" width="5" height="18" rx="1"/>
            <rect x="10" y="3" width="5" height="11" rx="1"/>
            <rect x="17" y="3" width="5" height="14" rx="1"/>
          </svg>
        </span>
        <span class="side-label" v-if="store.sideOpen">
          Kanban
          <kbd class="md-kbd">Ctrl K</kbd>
        </span>
      </button>

      <button
        class="side-item md-open-btn"
        :class="{ active: mdOpen }"
        @click="mdOpen = !mdOpen"
        :title="store.sideOpen ? 'Ctrl+M' : 'Editor Markdown (Ctrl+M)'"
      >
        <span class="side-icon">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
            <polyline points="14 2 14 8 20 8"/>
            <line x1="16" y1="13" x2="8" y2="13"/>
            <line x1="16" y1="17" x2="8" y2="17"/>
            <polyline points="10 9 9 9 8 9"/>
          </svg>
        </span>
        <span class="side-label" v-if="store.sideOpen">
          Markdown
          <kbd class="md-kbd">Ctrl M</kbd>
        </span>
      </button>
    </div>

    <KanbanBoard v-model:open="kanbanOpen" />
    <MarkdownEditor v-model:open="mdOpen" />
  </aside>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue'
import { useStore } from '../store/index.js'
import MarkdownEditor from './MarkdownEditor.vue'
import KanbanBoard from './KanbanBoard.vue'

const store = useStore()
const mdOpen = ref(false)
const kanbanOpen = ref(false)

function maybeClose() {
  if (window.innerWidth < 768) store.sideOpen = false
}

function onKeydown(e) {
  if (!(e.ctrlKey || e.metaKey)) return
  if (e.key === 'm') { e.preventDefault(); mdOpen.value = !mdOpen.value }
  if (e.key === 'k') { e.preventDefault(); kanbanOpen.value = !kanbanOpen.value }
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>
