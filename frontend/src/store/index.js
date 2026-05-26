import { defineStore } from 'pinia'
import { ref } from 'vue'

const API = '/api'

export const useStore = defineStore('main', () => {
  const categories = ref([])
  const shortcuts = ref([])
  const sideOpen = ref(true)

  async function fetchCategories() {
    const r = await fetch(`${API}/categories/`)
    categories.value = await r.json()
  }

  async function fetchShortcuts(categoryId = null) {
    const url = categoryId ? `${API}/shortcuts/?category_id=${categoryId}` : `${API}/shortcuts/`
    const r = await fetch(url)
    shortcuts.value = await r.json()
  }

  async function saveCategory(data, id = null) {
    const method = id ? 'PUT' : 'POST'
    const url = id ? `${API}/categories/${id}` : `${API}/categories/`
    await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
    await fetchCategories()
  }

  async function deleteCategory(id) {
    await fetch(`${API}/categories/${id}`, { method: 'DELETE' })
    await fetchCategories()
  }

  async function saveShortcut(data, id = null) {
    const method = id ? 'PUT' : 'POST'
    const url = id ? `${API}/shortcuts/${id}` : `${API}/shortcuts/`
    await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) })
    await fetchShortcuts()
  }

  async function deleteShortcut(id) {
    await fetch(`${API}/shortcuts/${id}`, { method: 'DELETE' })
    await fetchShortcuts()
  }

  return { categories, shortcuts, sideOpen, fetchCategories, fetchShortcuts, saveCategory, deleteCategory, saveShortcut, deleteShortcut }
})
