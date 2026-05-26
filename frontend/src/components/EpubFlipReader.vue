<template>
  <div class="epub-reader" @keydown="onKey" tabindex="0" ref="readerRoot">

    <!-- Header -->
    <div class="reader-header">
      <button class="icon-btn" @click="$emit('close')" title="Fechar">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
      </button>

      <div class="header-title">{{ bookTitle || title }}</div>

      <div class="header-tools">
        <button class="icon-btn" @click="showToc = !showToc" :class="{ active: showToc }" title="Sumário">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="8" y1="6" x2="20" y2="6"/><line x1="8" y1="12" x2="20" y2="12"/><line x1="8" y1="18" x2="20" y2="18"/><circle cx="3.5" cy="6" r="1" fill="currentColor"/><circle cx="3.5" cy="12" r="1" fill="currentColor"/><circle cx="3.5" cy="18" r="1" fill="currentColor"/></svg>
        </button>
        <button class="text-btn" @click="changeFontSize(-1)" title="Diminuir fonte">A−</button>
        <button class="text-btn" @click="changeFontSize(1)" title="Aumentar fonte">A+</button>
        <button class="icon-btn" @click="toggleTheme" title="Alternar tema">
          <svg v-if="isDark" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
        </button>
      </div>
    </div>

    <!-- Body -->
    <div class="reader-body" :class="{ 'theme-dark': isDark }">

      <!-- TOC -->
      <Transition name="toc-slide">
        <aside class="toc-panel" v-if="showToc">
          <div class="toc-heading">Sumário</div>
          <ul class="toc-list">
            <li
              v-for="item in toc"
              :key="item.id"
              class="toc-item"
              :style="{ paddingLeft: `${(item.level || 0) * 14 + 16}px` }"
              @click="gotoToc(item)"
            >{{ item.label }}</li>
          </ul>
        </aside>
      </Transition>

      <!-- Content area -->
      <div class="content-area">

        <!-- Slide wrapper: this element slides on navigation -->
        <div
          class="slide-wrapper"
          :class="slideClass"
          ref="slideWrapperEl"
        >
          <div class="epub-mount" ref="epubMount"></div>
        </div>

        <!-- Nav buttons -->
        <button class="nav-btn nav-prev" @click="prevPage" :disabled="navigating" title="Anterior (←)">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <button class="nav-btn nav-next" @click="nextPage" :disabled="navigating" title="Próxima (→)">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>

      </div>
    </div>

    <!-- Footer -->
    <div class="reader-footer">
      <span class="progress-pct">{{ Math.round(progress) }}%</span>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
    </div>

    <!-- Loading -->
    <Transition name="fade">
      <div class="loading-screen" v-if="loading">
        <div class="spinner"></div>
        <span>Carregando…</span>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import ePub from 'epubjs'

const props = defineProps({
  url: { type: String, required: true },
  bookTitle: { type: String, default: '' },
})
defineEmits(['close'])

const readerRoot   = ref(null)
const epubMount    = ref(null)
const slideWrapperEl = ref(null)

const title      = ref('')
const toc        = ref([])
const showToc    = ref(false)
const progress   = ref(0)
const loading    = ref(true)
const isDark     = ref(false)
const fontSize   = ref(100)
const navigating = ref(false)
const slideClass = ref('')

let book    = null
let rendition = null

const SLIDE_MS = 280

onMounted(async () => {
  await nextTick()
  readerRoot.value?.focus()
  await initReader()
})

onUnmounted(cleanup)

watch(() => props.url, async () => {
  cleanup()
  await nextTick()
  await initReader()
})

function cleanup() {
  if (rendition) { rendition.destroy(); rendition = null }
  if (book)      { book.destroy();      book = null }
  loading.value = true
}

async function initReader() {
  if (!epubMount.value) return
  loading.value = true

  try {
    book = ePub(props.url)

    rendition = book.renderTo(epubMount.value, {
      width:  '100%',
      height: '100%',
      spread: 'none',
      flow:   'paginated',
    })

    applyTheme()

    await rendition.display()

    // Mostra o conteúdo assim que a primeira página renderizar
    loading.value = false

    // Operações pesadas em background — não bloqueiam a UI
    book.ready.then(async () => {
      const meta = book.packaging?.metadata
      title.value = meta?.title || props.bookTitle || 'Livro'

      const nav = await book.navigation
      toc.value = flattenToc(nav?.toc || [])

      // Gera localizações em background para a barra de progresso
      book.locations.generate(1024)
    }).catch(err => console.warn('book.ready error:', err))

    rendition.on('locationChanged', loc => {
      if (book.locations?.length()) {
        const pct = book.locations.percentageFromCfi(loc.start.cfi)
        if (typeof pct === 'number') progress.value = Math.round(pct * 100)
      }
    })

  } catch (err) {
    console.error('epubjs error:', err)
    loading.value = false
  }
}

// ── Slide animation ───────────────────────────────────────────────
async function slide(direction) {
  if (navigating.value || !rendition) return
  navigating.value = true

  // Phase 1: slide current page out
  slideClass.value = direction === 'next' ? 'slide-out-left' : 'slide-out-right'
  await wait(SLIDE_MS)

  // Navigate (epubjs renders new content while iframe is "off screen")
  if (direction === 'next') await rendition.next()
  else                      await rendition.prev()

  // Phase 2: position the incoming page on the opposite side (instant, no transition)
  slideClass.value = direction === 'next' ? 'slide-in-right-instant' : 'slide-in-left-instant'
  await nextTick()

  // Phase 3: slide new page in
  slideClass.value = direction === 'next' ? 'slide-in-right' : 'slide-in-left'
  await wait(SLIDE_MS)

  slideClass.value = ''
  navigating.value = false
}

async function nextPage() { await slide('next') }
async function prevPage() { await slide('prev') }

async function gotoToc(item) {
  showToc.value = false
  await rendition?.display(item.href)
}

function changeFontSize(delta) {
  fontSize.value = Math.min(200, Math.max(70, fontSize.value + delta * 10))
  rendition?.themes.fontSize(`${fontSize.value}%`)
}

function toggleTheme() {
  isDark.value = !isDark.value
  applyTheme()
}

function applyTheme() {
  if (!rendition) return
  if (isDark.value) {
    rendition.themes.override('color',      '#d4d4d4')
    rendition.themes.override('background', '#1e1e2e')
  } else {
    rendition.themes.override('color',      '#1a1a1a')
    rendition.themes.override('background', '#ffffff')
  }
}

function flattenToc(items, level = 0) {
  const out = []
  for (const item of items) {
    out.push({ ...item, level })
    if (item.subitems?.length) out.push(...flattenToc(item.subitems, level + 1))
  }
  return out
}

function onKey(e) {
  if (e.key === 'ArrowRight' || e.key === 'PageDown') nextPage()
  if (e.key === 'ArrowLeft'  || e.key === 'PageUp')   prevPage()
}

function wait(ms) { return new Promise(r => setTimeout(r, ms)) }
</script>

<style scoped>
/* ── Shell ───────────────────────────────────── */
.epub-reader {
  display: flex;
  flex-direction: column;
  width: 100%;
  height: 100%;
  background: #111827;
  color: #e5e7eb;
  font-family: system-ui, sans-serif;
  outline: none;
  overflow: hidden;
  position: relative;
}

/* ── Header ──────────────────────────────────── */
.reader-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 16px;
  height: 48px;
  background: #0d1117;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}

.header-title {
  flex: 1;
  text-align: center;
  font-size: 0.83rem;
  font-weight: 600;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-tools { display: flex; align-items: center; gap: 4px; }

.icon-btn, .text-btn {
  background: transparent;
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 6px;
  color: #9ca3af;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.icon-btn { width: 32px; height: 32px; }
.text-btn  { padding: 0 8px; height: 32px; font-size: 0.72rem; font-weight: 700; letter-spacing: 0.02em; }

.icon-btn:hover, .text-btn:hover { background: rgba(255,255,255,0.08); color: #f3f4f6; }
.icon-btn.active { background: rgba(99,102,241,0.2); border-color: rgba(99,102,241,0.4); color: #818cf8; }

/* ── Body ────────────────────────────────────── */
.reader-body {
  flex: 1;
  display: flex;
  overflow: hidden;
  background: #f9fafb;
  transition: background 0.3s;
}
.reader-body.theme-dark { background: #1e1e2e; }

/* ── TOC ─────────────────────────────────────── */
.toc-panel {
  width: 240px;
  min-width: 240px;
  background: #0d1117;
  border-right: 1px solid rgba(255,255,255,0.07);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.toc-heading {
  padding: 14px 16px 10px;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #6b7280;
  border-bottom: 1px solid rgba(255,255,255,0.05);
}
.toc-list {
  list-style: none;
  margin: 0;
  padding: 6px 0;
  overflow-y: auto;
  flex: 1;
}
.toc-item {
  padding: 9px 0;
  padding-right: 12px;
  font-size: 0.82rem;
  color: #9ca3af;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  transition: color 0.15s, background 0.15s;
}
.toc-item:hover { color: #f3f4f6; background: rgba(255,255,255,0.04); }

.toc-slide-enter-active, .toc-slide-leave-active { transition: width 0.25s ease, opacity 0.25s ease; overflow: hidden; }
.toc-slide-enter-from, .toc-slide-leave-to { width: 0; opacity: 0; min-width: 0; }
.toc-slide-enter-to, .toc-slide-leave-from { width: 240px; opacity: 1; }

/* ── Content area ────────────────────────────── */
.content-area {
  flex: 1;
  position: relative;
  overflow: hidden;
}

/* ── Slide wrapper ───────────────────────────── */
.slide-wrapper {
  width: 100%;
  height: 100%;
  will-change: transform;
}

/* Transitions */
.slide-wrapper.slide-out-left  { transition: transform 0.28s ease-in;  transform: translateX(-100%); }
.slide-wrapper.slide-out-right { transition: transform 0.28s ease-in;  transform: translateX(100%);  }
.slide-wrapper.slide-in-right-instant { transition: none; transform: translateX(100%);  }
.slide-wrapper.slide-in-left-instant  { transition: none; transform: translateX(-100%); }
.slide-wrapper.slide-in-right  { transition: transform 0.28s ease-out; transform: translateX(0); }
.slide-wrapper.slide-in-left   { transition: transform 0.28s ease-out; transform: translateX(0); }

/* ── EPUB iframe ─────────────────────────────── */
.epub-mount {
  width: 100%;
  height: 100%;
}
.epub-mount :deep(iframe) {
  width: 100% !important;
  height: 100% !important;
  border: none;
  display: block;
}

/* ── Nav buttons ─────────────────────────────── */
.nav-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: rgba(0,0,0,0.12);
  color: #374151;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, color 0.2s, transform 0.2s;
  z-index: 10;
}
.theme-dark .nav-btn { background: rgba(255,255,255,0.08); color: #9ca3af; }
.nav-btn:hover:not(:disabled) { background: rgba(99,102,241,0.2); color: #6366f1; transform: translateY(-50%) scale(1.1); }
.nav-btn:disabled { opacity: 0.2; cursor: default; }
.nav-prev { left: 8px; }
.nav-next { right: 8px; }

/* ── Footer ──────────────────────────────────── */
.reader-footer {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: #0d1117;
  border-top: 1px solid rgba(255,255,255,0.07);
  flex-shrink: 0;
}
.progress-pct {
  font-size: 0.7rem;
  color: #4b5563;
  min-width: 34px;
  font-variant-numeric: tabular-nums;
}
.progress-track {
  flex: 1;
  height: 3px;
  background: rgba(255,255,255,0.07);
  border-radius: 2px;
  overflow: hidden;
}
.progress-fill {
  height: 100%;
  background: #6366f1;
  border-radius: 2px;
  transition: width 0.4s ease;
}

/* ── Loading ─────────────────────────────────── */
.loading-screen {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  background: rgba(17, 24, 39, 0.9);
  backdrop-filter: blur(6px);
  z-index: 50;
  font-size: 0.85rem;
  color: #6b7280;
}
.spinner {
  width: 32px; height: 32px;
  border: 3px solid rgba(99,102,241,0.15);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.75s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
