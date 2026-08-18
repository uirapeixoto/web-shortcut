<template>
  <div class="docs-page">
    <!-- Project grid -->
    <template v-if="!activeProject">
      <div class="page-header">
        <div>
          <h1 class="page-title">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
            Documentação Local
          </h1>
          <p class="page-subtitle">Cadastre pastas da máquina local para navegar e editar arquivos Markdown</p>
        </div>
        <button class="btn-add" @click="openProjectModal()">+ Novo Projeto</button>
      </div>

      <Transition name="fade">
        <div class="error-bar" v-if="errorMsg">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          {{ errorMsg }}
          <button @click="errorMsg = ''">×</button>
        </div>
      </Transition>

      <div class="projects-grid" v-if="projects.length">
        <div class="project-card" v-for="p in projects" :key="p.id" @click="openProject(p)">
          <div class="project-icon">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
          </div>
          <div class="project-info">
            <div class="project-name">{{ p.name }}</div>
            <div class="project-desc" v-if="p.description">{{ p.description }}</div>
            <div class="project-path">{{ p.local_path }}</div>
          </div>
          <div class="project-actions" @click.stop>
            <button class="action-btn edit-btn" title="Editar" @click="openProjectModal(p)">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
            </button>
            <button class="action-btn del-btn" title="Excluir" @click="deleteProject(p)">
              <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/></svg>
            </button>
          </div>
        </div>
      </div>

      <div class="empty-state" v-else-if="!isLoading">
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/></svg>
        <p>Nenhum projeto ainda. Cadastre uma pasta local para começar!</p>
      </div>
    </template>

    <!-- Project workspace -->
    <div class="docs-workspace" v-else>
      <div class="docs-tree-panel">
        <button class="back-btn" @click="closeProject">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
          Projetos
        </button>
        <div class="docs-tree-header">
          <strong>{{ activeProject.name }}</strong>
        </div>
        <Transition name="fade">
          <div class="error-bar error-bar--small" v-if="treeError">{{ treeError }}</div>
        </Transition>
        <ul class="tree-root" v-if="tree">
          <DocTreeNode
            v-for="child in tree.children"
            :key="child.path"
            :node="child"
            :active-path="activeFilePath"
            @open-file="openFile"
          />
        </ul>
        <div class="tree-empty" v-else-if="!treeError">Carregando árvore…</div>
      </div>

      <div class="docs-editor-area">
        <DocMarkdownPanel
          ref="panelRef"
          :file-path="activeFilePath"
          :file-name="activeFileName"
          :content="activeFileContent"
          :saving="isSaving"
          @save="saveFile"
        />
      </div>
    </div>

    <!-- Modal: create/edit project -->
    <div class="modal-overlay" v-if="showModal" @click.self="showModal = false">
      <div class="modal">
        <h3>{{ editingProject?.id ? 'Editar' : 'Novo' }} Projeto</h3>
        <label>Nome</label>
        <input v-model="form.name" placeholder="Ex: Documentação Backend" />
        <label>Caminho local</label>
        <input v-model="form.local_path" placeholder="/DATA/projetos/meu-app/docs" />
        <label>Descrição</label>
        <input v-model="form.description" placeholder="Breve descrição do projeto" />
        <p class="modal-hint" v-if="modalError">{{ modalError }}</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="showModal = false">Cancelar</button>
          <button class="btn-save" @click="saveProject">Salvar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import DocTreeNode from '../components/DocTreeNode.vue'
import DocMarkdownPanel from '../components/DocMarkdownPanel.vue'

const projects = ref([])
const isLoading = ref(true)
const errorMsg = ref('')

const showModal = ref(false)
const editingProject = ref(null)
const modalError = ref('')
const form = reactive({ name: '', local_path: '', description: '' })

const activeProject = ref(null)
const tree = ref(null)
const treeError = ref('')

const activeFilePath = ref('')
const activeFileName = ref('')
const activeFileContent = ref('')
const isSaving = ref(false)
const panelRef = ref(null)

onMounted(fetchProjects)

async function fetchProjects() {
  isLoading.value = true
  try {
    const r = await fetch('/api/projects')
    projects.value = await r.json()
  } catch {
    errorMsg.value = 'Erro ao carregar projetos'
  } finally {
    isLoading.value = false
  }
}

function openProjectModal(p = null) {
  editingProject.value = p
  modalError.value = ''
  Object.assign(form, p || { name: '', local_path: '', description: '' })
  showModal.value = true
}

async function saveProject() {
  if (!form.name.trim() || !form.local_path.trim()) {
    modalError.value = 'Nome e caminho são obrigatórios'
    return
  }
  modalError.value = ''
  const isEdit = !!editingProject.value?.id
  const url = isEdit ? `/api/projects/${editingProject.value.id}` : '/api/projects'
  try {
    const r = await fetch(url, {
      method: isEdit ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: form.name, local_path: form.local_path, description: form.description }),
    })
    if (!r.ok) {
      const err = await r.json().catch(() => ({}))
      modalError.value = err.detail || 'Erro ao salvar projeto'
      return
    }
    showModal.value = false
    await fetchProjects()
  } catch {
    modalError.value = 'Erro de conexão ao salvar projeto'
  }
}

async function deleteProject(p) {
  if (!confirm(`Remover projeto "${p.name}"? Os arquivos no disco não serão apagados.`)) return
  try {
    await fetch(`/api/projects/${p.id}`, { method: 'DELETE' })
    projects.value = projects.value.filter(x => x.id !== p.id)
  } catch {
    errorMsg.value = 'Erro ao excluir projeto'
  }
}

async function openProject(p) {
  activeProject.value = p
  activeFilePath.value = ''
  activeFileName.value = ''
  activeFileContent.value = ''
  await loadTree()
}

function closeProject() {
  activeProject.value = null
  tree.value = null
  activeFilePath.value = ''
}

async function loadTree() {
  treeError.value = ''
  tree.value = null
  try {
    const r = await fetch(`/api/projects/${activeProject.value.id}/tree`)
    if (!r.ok) {
      const err = await r.json().catch(() => ({}))
      treeError.value = err.detail || 'Erro ao carregar árvore de arquivos'
      return
    }
    tree.value = await r.json()
  } catch {
    treeError.value = 'Erro de conexão ao carregar árvore'
  }
}

async function openFile(path) {
  try {
    const r = await fetch(`/api/projects/${activeProject.value.id}/file?path=${encodeURIComponent(path)}`)
    if (!r.ok) {
      const err = await r.json().catch(() => ({}))
      errorMsg.value = err.detail || 'Erro ao abrir arquivo'
      return
    }
    const data = await r.json()
    activeFilePath.value = path
    activeFileName.value = path.split('/').pop()
    activeFileContent.value = data.content
  } catch {
    errorMsg.value = 'Erro de conexão ao abrir arquivo'
  }
}

async function saveFile(content) {
  if (!activeFilePath.value) return
  isSaving.value = true
  try {
    const r = await fetch(`/api/projects/${activeProject.value.id}/file?path=${encodeURIComponent(activeFilePath.value)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })
    if (!r.ok) {
      const err = await r.json().catch(() => ({}))
      errorMsg.value = err.detail || 'Erro ao salvar arquivo'
      return
    }
    activeFileContent.value = content
    panelRef.value?.markSaved()
  } catch {
    errorMsg.value = 'Erro de conexão ao salvar arquivo'
  } finally {
    isSaving.value = false
  }
}
</script>

<style scoped>
.docs-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 32px 24px;
  height: calc(100vh - var(--top-h) - 64px);
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 28px;
}
.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 6px;
}
.page-subtitle { color: var(--text2); font-size: 0.9rem; margin: 0; }

.btn-add {
  padding: 9px 18px;
  border-radius: 10px;
  border: none;
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: var(--trans);
  white-space: nowrap;
}
.btn-add:hover { background: var(--accent2); }

.error-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  border-radius: 8px;
  font-size: 0.85rem;
  color: #ef4444;
  margin-bottom: 20px;
}
.error-bar--small { margin: 0 10px 8px; padding: 6px 10px; font-size: 0.75rem; }
.error-bar button { margin-left: auto; background: none; border: none; color: #ef4444; cursor: pointer; font-size: 1.1rem; line-height: 1; }
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 16px;
}
.project-card {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius);
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: var(--bg2);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.project-card:hover { transform: translateY(-3px); box-shadow: var(--shadow); }
.project-icon {
  flex-shrink: 0;
  width: 44px; height: 44px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, var(--accent), var(--accent2));
  color: #fff;
}
.project-info { flex: 1; min-width: 0; }
.project-name { font-weight: 700; font-size: 0.95rem; margin-bottom: 2px; }
.project-desc { font-size: 0.8rem; color: var(--text2); margin-bottom: 4px; }
.project-path {
  font-family: monospace;
  font-size: 0.72rem;
  color: var(--text2);
  opacity: 0.7;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.project-actions { display: flex; gap: 4px; flex-shrink: 0; }
.action-btn {
  width: 26px; height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.06);
  color: var(--text2);
}
.edit-btn:hover { background: rgba(99, 102, 241, 0.2); color: var(--accent); }
.del-btn:hover { background: rgba(239, 68, 68, 0.15); color: #ef4444; }

.empty-state {
  text-align: center;
  padding: 60px 0;
  color: var(--text2);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.empty-state p { font-size: 0.95rem; margin: 0; }

/* Workspace */
.docs-workspace {
  flex: 1;
  display: flex;
  gap: 16px;
  min-height: 0;
}
.docs-tree-panel {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  background: var(--bg2);
  border-radius: var(--radius);
  border: 1px solid rgba(255, 255, 255, 0.06);
  overflow: hidden;
}
.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 14px;
  border: none;
  background: transparent;
  color: var(--text2);
  font-size: 0.8rem;
  cursor: pointer;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.back-btn:hover { color: var(--text); }
.docs-tree-header {
  padding: 8px 14px;
  font-size: 0.85rem;
  color: var(--text);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}
.tree-root {
  flex: 1;
  overflow-y: auto;
  padding: 8px;
  margin: 0;
}
.tree-empty { padding: 14px; color: var(--text2); font-size: 0.8rem; }

.docs-editor-area {
  flex: 1;
  min-width: 0;
}

@media (max-width: 768px) {
  .docs-workspace { flex-direction: column; }
  .docs-tree-panel { width: 100%; max-height: 240px; }
}
</style>
