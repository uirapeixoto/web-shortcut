<template>
  <div class="dm-panel">
    <div class="dm-toolbar">
      <span class="dm-title">
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <span class="dm-filename">{{ fileName || 'Nenhum arquivo selecionado' }}</span>
        <span class="dm-dirty-dot" v-if="dirty" title="Alterações não salvas"></span>
      </span>

      <div class="dm-mode-tabs" v-if="filePath">
        <button :class="{ active: mode === 'edit' }" @click="mode = 'edit'" title="Somente editor">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          Editar
        </button>
        <button :class="{ active: mode === 'split' }" @click="mode = 'split'" title="Split view">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="18" height="18" rx="2"/><line x1="12" y1="3" x2="12" y2="21"/></svg>
          Split
        </button>
        <button :class="{ active: mode === 'preview' }" @click="mode = 'preview'" title="Somente preview">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
          Preview
        </button>
      </div>

      <div class="dm-toolbar-actions" v-if="filePath">
        <span class="dm-save-msg" :class="{ visible: !!saveMsg }">{{ saveMsg }}</span>
        <button class="dm-btn-save" :disabled="!dirty || saving" @click="save" title="Salvar (Ctrl+S)">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
          {{ saving ? 'Salvando…' : 'Salvar' }}
        </button>
      </div>
    </div>

    <div v-if="filePath && mode !== 'preview'" class="dm-format-bar">
      <div class="fmt-group">
        <button @click="fmt('**', '**')" title="Negrito (Ctrl+B)"><b>B</b></button>
        <button @click="fmt('*', '*')" title="Itálico (Ctrl+I)"><i>I</i></button>
        <button @click="fmt('~~', '~~')" title="Tachado"><s>S</s></button>
      </div>
      <div class="fmt-sep"></div>
      <div class="fmt-group">
        <button @click="insertHeading(1)" title="Cabeçalho 1">H1</button>
        <button @click="insertHeading(2)" title="Cabeçalho 2">H2</button>
        <button @click="insertHeading(3)" title="Cabeçalho 3">H3</button>
      </div>
      <div class="fmt-sep"></div>
      <div class="fmt-group">
        <button @click="fmt('`', '`')" title="Código inline">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>
        </button>
        <button @click="insertBlock('```\n', '\n```')" title="Bloco de código">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
        </button>
        <button @click="insertMermaid" title="Diagrama Mermaid" class="fmt-mermaid">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><line x1="12" y1="7" x2="5" y2="17"/><line x1="12" y1="7" x2="19" y2="17"/></svg>
          Mermaid
        </button>
      </div>
      <div class="fmt-sep"></div>
      <div class="fmt-group">
        <button @click="insertLine('- ')" title="Lista não ordenada">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
        </button>
        <button @click="insertLine('1. ')" title="Lista ordenada">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="10" y1="6" x2="21" y2="6"/><line x1="10" y1="12" x2="21" y2="12"/><line x1="10" y1="18" x2="21" y2="18"/><path d="M4 6h1v4"/><path d="M4 10h2"/><path d="M6 18H4c0-1 2-2 2-3s-1-1.5-2-1"/></svg>
        </button>
        <button @click="insertLine('> ')" title="Citação">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/></svg>
        </button>
        <button @click="insertLink" title="Link">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
        </button>
        <button @click="insertLine('---\n')" title="Linha divisória">—</button>
      </div>
    </div>

    <div class="dm-body" :class="{ 'dm-body--split': mode === 'split', 'dm-body--preview': mode === 'preview' }">
      <div v-if="!filePath" class="dm-empty">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
        <p>Selecione um arquivo .md na árvore ao lado</p>
      </div>

      <template v-else>
        <div v-if="mode !== 'preview'" class="dm-editor-pane">
          <textarea
            ref="textareaRef"
            class="dm-textarea"
            v-model="source"
            spellcheck="false"
            @keydown.tab.prevent="handleTab"
            @keydown.ctrl.b.prevent="fmt('**', '**')"
            @keydown.ctrl.i.prevent="fmt('*', '*')"
            @keydown.ctrl.s.prevent="save"
            @keydown.meta.s.prevent="save"
          />
        </div>

        <div v-if="mode !== 'edit'" class="dm-preview-pane">
          <div v-if="rendering" class="dm-loading">
            <div class="dm-spinner"></div>
            <span>Renderizando...</span>
          </div>
          <div v-else class="dm-preview" ref="previewRef" v-html="rendered" />
        </div>
      </template>
    </div>

    <div class="dm-statusbar" v-if="filePath">
      <span class="dm-stats">{{ lineCount }} linhas &middot; {{ wordCount }} palavras</span>
      <span class="dm-path">{{ filePath }}</span>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  filePath: { type: String, default: '' },
  fileName: { type: String, default: '' },
  content: { type: String, default: '' },
  saving: { type: Boolean, default: false },
})
const emit = defineEmits(['save'])

const mode = ref('split')
const source = ref(props.content)
const dirty = ref(false)
const saveMsg = ref('')
const textareaRef = ref(null)
const previewRef = ref(null)
const rendering = ref(false)
const rendered = ref('')

marked.setOptions({ breaks: true, gfm: true })

let mermaid = null
async function loadMermaid() {
  if (!mermaid) {
    const mod = await import('mermaid')
    mermaid = mod.default
    mermaid.initialize({ startOnLoad: false, theme: 'dark', darkMode: true, securityLevel: 'loose' })
  }
  return mermaid
}

watch(() => props.content, (val) => {
  source.value = val
  dirty.value = false
  if (mode.value !== 'edit') renderMarkdown()
})

watch(source, (val) => {
  dirty.value = val !== props.content
  if (mode.value === 'edit') return
  clearTimeout(renderTimer)
  renderTimer = setTimeout(() => renderMarkdown(), 350)
})
let renderTimer = null

watch(mode, async (val) => {
  if (val !== 'edit') await renderMarkdown()
})

const lineCount = computed(() => source.value.split('\n').length)
const wordCount = computed(() => source.value.trim() ? source.value.trim().split(/\s+/).length : 0)

async function renderMarkdown() {
  rendering.value = true
  rendered.value = marked.parse(source.value || '')
  rendering.value = false
  await nextTick()
  await renderMermaid()
}

async function renderMermaid() {
  if (!previewRef.value) return
  const blocks = previewRef.value.querySelectorAll('code.language-mermaid')
  if (!blocks.length) return
  const mer = await loadMermaid()
  for (const block of blocks) {
    const code = block.textContent
    const id = 'dm-mermaid-' + Math.random().toString(36).slice(2)
    try {
      const { svg } = await mer.render(id, code)
      const wrapper = document.createElement('div')
      wrapper.className = 'mermaid-diagram'
      wrapper.innerHTML = svg
      block.parentElement.replaceWith(wrapper)
    } catch (e) {
      const errEl = document.createElement('div')
      errEl.className = 'mermaid-error'
      errEl.textContent = '⚠ Erro no diagrama: ' + e.message
      block.parentElement.replaceWith(errEl)
    }
  }
}

function save() {
  if (!dirty.value || props.saving) return
  emit('save', source.value)
}

function markSaved() {
  saveMsg.value = '✓ Salvo!'
  setTimeout(() => (saveMsg.value = ''), 2000)
}
defineExpose({ markSaved })

function fmt(before, after) {
  const el = textareaRef.value
  if (!el) return
  const { selectionStart: s, selectionEnd: e } = el
  const sel = source.value.slice(s, e) || 'texto'
  source.value = source.value.slice(0, s) + before + sel + after + source.value.slice(e)
  nextTick(() => {
    el.focus()
    el.setSelectionRange(s + before.length, s + before.length + sel.length)
  })
}

function insertBlock(before, after) {
  const el = textareaRef.value
  if (!el) return
  const { selectionStart: s } = el
  source.value = source.value.slice(0, s) + before + after + source.value.slice(s)
  nextTick(() => { el.focus(); el.setSelectionRange(s + before.length, s + before.length) })
}

function insertMermaid() {
  insertBlock('\n```mermaid\ngraph TD\n  A[Início] --> B[Fim]\n```\n', '')
}

function insertHeading(level) {
  const el = textareaRef.value
  if (!el) return
  const { selectionStart: s } = el
  const lineStart = source.value.lastIndexOf('\n', s - 1) + 1
  const prefix = '#'.repeat(level) + ' '
  source.value = source.value.slice(0, lineStart) + prefix + source.value.slice(lineStart)
  nextTick(() => el.focus())
}

function insertLine(prefix) {
  const el = textareaRef.value
  if (!el) return
  const { selectionStart: s } = el
  const lineStart = source.value.lastIndexOf('\n', s - 1) + 1
  source.value = source.value.slice(0, lineStart) + prefix + source.value.slice(lineStart)
  nextTick(() => el.focus())
}

function insertLink() {
  const url = prompt('URL do link:')
  if (!url) return
  const label = prompt('Texto do link:', 'link') || 'link'
  fmt(`[${label}](`, `${url})`)
}

function handleTab(e) {
  const el = textareaRef.value
  const { selectionStart: s, selectionEnd: end } = el
  source.value = source.value.slice(0, s) + '  ' + source.value.slice(end)
  nextTick(() => el.setSelectionRange(s + 2, s + 2))
}
</script>

<style scoped>
.dm-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--bg2);
  border-radius: var(--radius);
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.06);
}

.dm-toolbar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 10px 14px;
  background: var(--bg3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-wrap: wrap;
}
.dm-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--text);
  min-width: 0;
}
.dm-filename { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 260px; }
.dm-dirty-dot {
  width: 7px; height: 7px;
  border-radius: 50%;
  background: #f59e0b;
  flex-shrink: 0;
}

.dm-mode-tabs { display: flex; gap: 4px; margin-left: auto; }
.dm-mode-tabs button {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text2);
  font-size: 0.78rem;
  cursor: pointer;
  transition: var(--trans);
}
.dm-mode-tabs button:hover { background: rgba(255, 255, 255, 0.06); color: var(--text); }
.dm-mode-tabs button.active { background: var(--accent); color: #fff; }

.dm-toolbar-actions { display: flex; align-items: center; gap: 10px; }
.dm-save-msg { font-size: 0.78rem; color: #4ade80; opacity: 0; transition: opacity 0.2s; }
.dm-save-msg.visible { opacity: 1; }
.dm-btn-save {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 8px;
  border: none;
  background: var(--accent);
  color: #fff;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: var(--trans);
}
.dm-btn-save:hover:not(:disabled) { background: var(--accent2); }
.dm-btn-save:disabled { opacity: 0.4; cursor: default; }

.dm-format-bar {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  flex-wrap: wrap;
}
.fmt-group { display: flex; gap: 2px; }
.fmt-sep { width: 1px; height: 16px; background: rgba(255, 255, 255, 0.1); }
.dm-format-bar button {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 7px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--text2);
  font-size: 0.75rem;
  cursor: pointer;
}
.dm-format-bar button:hover { background: rgba(255, 255, 255, 0.08); color: var(--text); }
.fmt-mermaid { color: var(--accent2) !important; }

.dm-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  min-height: 0;
}
.dm-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: var(--text2);
}
.dm-empty p { margin: 0; font-size: 0.9rem; }

.dm-editor-pane, .dm-preview-pane { flex: 1; min-width: 0; overflow: auto; }
.dm-body--split .dm-editor-pane { border-right: 1px solid rgba(255, 255, 255, 0.06); }

.dm-textarea {
  width: 100%;
  height: 100%;
  min-height: 300px;
  border: none;
  outline: none;
  resize: none;
  background: transparent;
  color: var(--text);
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 0.86rem;
  line-height: 1.6;
  padding: 16px;
  box-sizing: border-box;
}

.dm-preview-pane { padding: 20px 24px; }
.dm-preview { color: var(--text); line-height: 1.65; font-size: 0.92rem; }
.dm-preview :deep(h1), .dm-preview :deep(h2), .dm-preview :deep(h3) { margin-top: 1.2em; }
.dm-preview :deep(pre) {
  background: rgba(0, 0, 0, 0.3);
  padding: 12px 14px;
  border-radius: 8px;
  overflow-x: auto;
}
.dm-preview :deep(code) {
  background: rgba(255, 255, 255, 0.08);
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.85em;
}
.dm-preview :deep(pre code) { background: none; padding: 0; }
.dm-preview :deep(blockquote) {
  border-left: 3px solid var(--accent);
  margin: 0.8em 0;
  padding: 2px 14px;
  color: var(--text2);
}
.dm-preview :deep(table) { border-collapse: collapse; width: 100%; }
.dm-preview :deep(th), .dm-preview :deep(td) {
  border: 1px solid rgba(255, 255, 255, 0.12);
  padding: 6px 10px;
}
.dm-preview :deep(.mermaid-diagram) { display: flex; justify-content: center; margin: 16px 0; }
.dm-preview :deep(.mermaid-error) {
  color: #f87171;
  font-size: 0.85rem;
  padding: 10px;
  background: rgba(239, 68, 68, 0.08);
  border-radius: 8px;
}

.dm-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 10px;
  height: 100%;
  color: var(--text2);
}
.dm-spinner {
  width: 24px; height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.15);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: dm-spin 0.8s linear infinite;
}
@keyframes dm-spin { to { transform: rotate(360deg); } }

.dm-statusbar {
  display: flex;
  justify-content: space-between;
  padding: 6px 14px;
  background: var(--bg3);
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 0.72rem;
  color: var(--text2);
}
.dm-path { font-family: monospace; opacity: 0.8; }
</style>
