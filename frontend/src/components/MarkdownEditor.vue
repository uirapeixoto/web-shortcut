<template>
  <Teleport to="body">
    <Transition name="md-fade">
      <div v-if="open" class="md-overlay" @click.self="close" @keydown.esc.window="close">
        <div
          class="md-panel"
          :class="{
            'md-panel--split': mode === 'split',
            'md-panel--preview': mode === 'preview',
            'md-panel--fullscreen': fullscreen
          }"
        >
          <!-- Toolbar -->
          <div class="md-toolbar">
            <span class="md-title">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
              Markdown
              <span class="md-saved-indicator" :class="{ visible: savedMsg }">{{ savedMsg }}</span>
            </span>

            <div class="md-mode-tabs">
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

            <div class="md-toolbar-actions">
              <button class="md-btn-icon" title="Novo documento (Ctrl+Shift+N)" @click="confirmNew">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="12" y1="18" x2="12" y2="12"/><line x1="9" y1="15" x2="15" y2="15"/></svg>
              </button>
              <button class="md-btn-icon" title="Copiar Markdown" @click="copyMarkdown">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
              </button>
              <button class="md-btn-icon" title="Baixar como .md" @click="downloadMarkdown">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
              </button>
              <button class="md-btn-icon" :title="fullscreen ? 'Sair de tela cheia' : 'Tela cheia'" @click="fullscreen = !fullscreen">
                <svg v-if="!fullscreen" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
                <svg v-else width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="10" y1="14" x2="3" y2="21"/><line x1="21" y1="3" x2="14" y2="10"/></svg>
              </button>
              <button class="md-btn-icon md-btn-close" title="Fechar (Esc)" @click="close">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
          </div>

          <!-- Format bar (hidden in preview-only mode) -->
          <div v-if="mode !== 'preview'" class="md-format-bar">
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
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/><path d="M15 21c3 0 7-1 7-8V5c0-1.25-.757-2.017-2-2h-4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2h.75c0 2.25.25 4-2.75 4v3c0 1 0 1 1 1z"/></svg>
              </button>
              <button @click="insertLink" title="Link">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg>
              </button>
              <button @click="insertLine('---\n')" title="Linha divisória">—</button>
            </div>
          </div>

          <!-- Body -->
          <div class="md-body">
            <div v-if="mode !== 'preview'" class="md-editor-pane">
              <textarea
                ref="textareaRef"
                class="md-textarea"
                v-model="source"
                spellcheck="false"
                @keydown.tab.prevent="handleTab"
                @keydown.ctrl.b.prevent="fmt('**', '**')"
                @keydown.ctrl.i.prevent="fmt('*', '*')"
                placeholder="Escreva seu Markdown aqui...&#10;&#10;Use ```mermaid para diagramas"
              />
            </div>

            <div v-if="mode !== 'edit'" class="md-preview-pane">
              <div v-if="rendering" class="md-loading">
                <div class="md-spinner"></div>
                <span>Renderizando...</span>
              </div>
              <div v-else class="md-preview" ref="previewRef" v-html="rendered" />
            </div>
          </div>

          <!-- Status bar -->
          <div class="md-statusbar">
            <span class="md-stats">
              {{ lineCount }} linhas &middot; {{ wordCount }} palavras &middot; {{ source.length }} chars
            </span>
            <span class="md-storage-hint" v-if="!savedMsg">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><polyline points="17 21 17 13 7 13 7 21"/><polyline points="7 3 7 8 15 8"/></svg>
              Salvo automaticamente
            </span>
            <span v-if="savedMsg" class="md-copy-msg">{{ savedMsg }}</span>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { marked } from 'marked'

const STORAGE_KEY = 'md-editor-content'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['update:open'])

const defaultContent = `# Olá, Markdown! 👋

Escreva aqui seu conteúdo com suporte a **negrito**, *itálico*, \`código\` e muito mais.

## Diagrama Mermaid

\`\`\`mermaid
graph TD
  A[Início] --> B{Decisão}
  B -->|Sim| C[Resultado A]
  B -->|Não| D[Resultado B]
  C --> E[Fim]
  D --> E
\`\`\`

## Lista de tarefas

- [x] Suporte a Markdown
- [x] Diagramas Mermaid
- [x] Persistência automática (localStorage)
- [ ] Sua próxima ideia
`

const source = ref(localStorage.getItem(STORAGE_KEY) ?? defaultContent)
const mode = ref('split')
const fullscreen = ref(false)
const textareaRef = ref(null)
const previewRef = ref(null)
const savedMsg = ref('')
const rendering = ref(false)

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

const lineCount = computed(() => source.value.split('\n').length)
const wordCount = computed(() => source.value.trim() ? source.value.trim().split(/\s+/).length : 0)

const rendered = ref('')

async function renderMarkdown() {
  rendering.value = true
  rendered.value = marked.parse(source.value)
  rendering.value = false   // mostra o div antes de chamar renderMermaid, senão previewRef é null
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
    const id = 'mermaid-' + Math.random().toString(36).slice(2)
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

// Auto-save to localStorage with debounce
let saveTimer = null
watch(source, (val) => {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => {
    localStorage.setItem(STORAGE_KEY, val)
  }, 800)
})

// Render on source change
let renderTimer = null
watch(source, () => {
  if (mode.value === 'edit') return
  clearTimeout(renderTimer)
  renderTimer = setTimeout(() => renderMarkdown(), 350)
})

watch(mode, async (val) => {
  if (val !== 'edit') await renderMarkdown()
})

watch(() => props.open, async (val) => {
  if (val && mode.value !== 'edit') await renderMarkdown()
})

// Keyboard shortcut: Esc to close
function onKeydown(e) {
  if (e.key === 'Escape' && props.open) close()
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))

function close() { emit('update:open', false) }

function confirmNew() {
  if (source.value.trim() && !confirm('Descartar conteúdo atual e começar do zero?')) return
  source.value = ''
  localStorage.removeItem(STORAGE_KEY)
}

async function copyMarkdown() {
  await navigator.clipboard.writeText(source.value)
  savedMsg.value = '✓ Copiado!'
  setTimeout(() => savedMsg.value = '', 2000)
}

function downloadMarkdown() {
  const blob = new Blob([source.value], { type: 'text/markdown' })
  const a = document.createElement('a')
  a.href = URL.createObjectURL(blob)
  a.download = 'documento.md'
  a.click()
  URL.revokeObjectURL(a.href)
}

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
