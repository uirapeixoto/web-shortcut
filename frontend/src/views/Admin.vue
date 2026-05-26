<template>
  <div class="admin-page">
    <div class="admin-tabs">
      <button :class="{ active: tab === 'shortcuts' }" @click="tab = 'shortcuts'">🔗 Atalhos</button>
      <button :class="{ active: tab === 'categories' }" @click="tab = 'categories'">🗂 Categorias</button>
    </div>

    <!-- SHORTCUTS TAB -->
    <div v-if="tab === 'shortcuts'">
      <div class="admin-section-header">
        <h3>Atalhos</h3>
        <button class="btn-add" @click="openShortcut()">+ Novo</button>
      </div>
      <table class="admin-table">
        <thead><tr><th>Ícone</th><th>Nome</th><th>URL</th><th>Categoria</th><th></th></tr></thead>
        <tbody>
          <tr v-for="s in store.shortcuts" :key="s.id">
            <td>{{ s.icon }}</td>
            <td>{{ s.name }}</td>
            <td><a :href="s.url" target="_blank" class="url-link">{{ s.url }}</a></td>
            <td>{{ catName(s.category_id) }}</td>
            <td class="actions">
              <button class="btn-edit" @click="openShortcut(s)">✏</button>
              <button class="btn-del" @click="store.deleteShortcut(s.id)">🗑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- CATEGORIES TAB -->
    <div v-if="tab === 'categories'">
      <div class="admin-section-header">
        <h3>Categorias</h3>
        <button class="btn-add" @click="openCategory()">+ Nova</button>
      </div>
      <table class="admin-table">
        <thead><tr><th>Ícone</th><th>Nome</th><th>Cor</th><th></th></tr></thead>
        <tbody>
          <tr v-for="c in store.categories" :key="c.id">
            <td>{{ c.icon }}</td>
            <td>{{ c.name }}</td>
            <td><span class="color-dot" :style="{ background: c.color }"></span></td>
            <td class="actions">
              <button class="btn-edit" @click="openCategory(c)">✏</button>
              <button class="btn-del" @click="store.deleteCategory(c.id)">🗑</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- MODAL SHORTCUT -->
    <div class="modal-overlay" v-if="showShortcutModal" @click.self="showShortcutModal = false">
      <div class="modal">
        <h3>{{ editingShortcut?.id ? 'Editar' : 'Novo' }} Atalho</h3>
        <label>Nome</label>
        <input v-model="scForm.name" placeholder="Ex: GitHub" />
        <label>URL</label>
        <input v-model="scForm.url" placeholder="https://..." />
        <label>Descrição</label>
        <input v-model="scForm.description" placeholder="Breve descrição" />
        <label>Ícone (emoji)</label>
        <input v-model="scForm.icon" placeholder="🌐" maxlength="4" />
        <label>Cor</label>
        <input type="color" v-model="scForm.color" />
        <label>Categoria</label>
        <select v-model="scForm.category_id">
          <option v-for="c in store.categories" :key="c.id" :value="c.id">{{ c.icon }} {{ c.name }}</option>
        </select>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showShortcutModal = false">Cancelar</button>
          <button class="btn-save" @click="saveShortcut">Salvar</button>
        </div>
      </div>
    </div>

    <!-- MODAL CATEGORY -->
    <div class="modal-overlay" v-if="showCatModal" @click.self="showCatModal = false">
      <div class="modal">
        <h3>{{ editingCat?.id ? 'Editar' : 'Nova' }} Categoria</h3>
        <label>Nome</label>
        <input v-model="catForm.name" placeholder="Ex: Trabalho" />
        <label>Ícone (emoji)</label>
        <input v-model="catForm.icon" placeholder="🔗" maxlength="4" />
        <label>Cor</label>
        <input type="color" v-model="catForm.color" />
        <div class="modal-actions">
          <button class="btn-cancel" @click="showCatModal = false">Cancelar</button>
          <button class="btn-save" @click="saveCategory">Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useStore } from '../store/index.js'

const store = useStore()
const tab = ref('shortcuts')

const showShortcutModal = ref(false)
const editingShortcut = ref(null)
const scForm = reactive({ name: '', url: '', description: '', icon: '🌐', color: '#6366f1', category_id: null, order: 0 })

const showCatModal = ref(false)
const editingCat = ref(null)
const catForm = reactive({ name: '', icon: '🔗', color: '#6366f1', order: 0 })

function catName(id) {
  return store.categories.find(c => c.id === id)?.name || '—'
}

function openShortcut(s = null) {
  editingShortcut.value = s
  Object.assign(scForm, s || { name: '', url: '', description: '', icon: '🌐', color: '#6366f1', category_id: store.categories[0]?.id || null, order: 0 })
  showShortcutModal.value = true
}

async function saveShortcut() {
  await store.saveShortcut({ ...scForm }, editingShortcut.value?.id)
  showShortcutModal.value = false
}

function openCategory(c = null) {
  editingCat.value = c
  Object.assign(catForm, c || { name: '', icon: '🔗', color: '#6366f1', order: 0 })
  showCatModal.value = true
}

async function saveCategory() {
  await store.saveCategory({ ...catForm }, editingCat.value?.id)
  showCatModal.value = false
}

onMounted(() => store.fetchShortcuts())
</script>
