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

        <!-- Page flip book -->
        <div class="flip-book" ref="flipBook">
          <!-- Main content: always present -->
          <div class="page-layer page-main" ref="pageMainEl">
            <div class="epub-mount" ref="epubMount"></div>
          </div>

          <!-- Flip card: animated overlay during page turn -->
          <div
            v-if="flipping"
            class="page-layer flip-card"
            :class="[flipDir, { 'flip-card--turning': flipTurning }]"
          >
            <!-- Front (leaving page) -->
            <div class="flip-face flip-face--front">
              <div class="page-bg" :class="{ dark: isDark }"></div>
              <div class="page-lines" :class="{ dark: isDark }"></div>
              <div class="flip-edge-shadow flip-edge-shadow--right"></div>
            </div>
            <!-- Back (arriving page, seen when card is flipped over) -->
            <div class="flip-face flip-face--back">
              <div class="page-bg" :class="{ dark: isDark }"></div>
              <div class="page-lines" :class="{ dark: isDark }"></div>
              <div class="flip-edge-shadow flip-edge-shadow--left"></div>
            </div>
          </div>

          <!-- Shadow cast on the static page underneath -->
          <div
            v-if="flipping"
            class="flip-cast-shadow"
            :class="[flipDir, { 'flip-cast-shadow--spreading': flipTurning }]"
          ></div>
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
      <div class="footer-left">
        <span class="page-info" v-if="currentPage > 0">
          <span class="page-label">Pág.</span>
          <strong class="page-num">{{ currentPage }}</strong>
          <span class="page-total" v-if="totalPages > 0"> / {{ totalPages }}</span>
        </span>
      </div>
      <div class="progress-track">
        <div class="progress-fill" :style="{ width: progress + '%' }"></div>
      </div>
      <span class="progress-pct">{{ Math.round(progress) }}%</span>
    </div>

    <!-- Loading / Error overlay -->
    <Transition name="fade">
      <div class="loading-screen" v-if="loading || errorMsg">
        <template v-if="errorMsg">
          <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="1.5" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <span class="err-title">Não foi possível abrir o livro</span>
          <span class="err-msg">{{ errorMsg }}</span>
          <div class="err-actions">
            <button class="err-btn" @click="$emit('close')">Fechar</button>
            <button class="err-btn err-retry" @click="retryLoad">Tentar novamente</button>
          </div>
        </template>
        <template v-else>
          <div class="spinner"></div>
          <span>Carregando…</span>
          <button class="cancel-btn" @click="$emit('close')">Cancelar</button>
        </template>
      </div>
    </Transition>

  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import ePub from 'epubjs'

const props = defineProps({
  url:       { type: String,  required: true },
  bookTitle: { type: String,  default: '' },
  ebookId:   { type: Number,  default: null },
})
const emit = defineEmits(['close'])

const readerRoot  = ref(null)
const epubMount   = ref(null)
const flipBook    = ref(null)
const pageMainEl  = ref(null)

const title       = ref('')
const toc         = ref([])
const showToc     = ref(false)
const progress    = ref(0)
const loading     = ref(true)
const errorMsg    = ref('')
const isDark      = ref(false)
const fontSize    = ref(100)
const navigating  = ref(false)

// Flip state
const flipping    = ref(false)
const flipTurning = ref(false)  // triggers CSS transition
const flipDir     = ref('flip-next')

// Page numbers
const currentPage = ref(0)
const totalPages  = ref(0)

let book      = null
let rendition = null
let saveTimer = null
let lastLoc   = null

const FLIP_MS = 500   // must match CSS transition duration

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
  clearTimeout(saveTimer)
  saveTimer = null
  lastLoc   = null
  if (rendition) { rendition.destroy(); rendition = null }
  if (book)      { book.destroy();      book = null }
  loading.value    = true
  errorMsg.value   = ''
  currentPage.value = 0
  totalPages.value  = 0
}

async function retryLoad() {
  cleanup()
  await nextTick()
  await initReader()
}

const LOAD_TIMEOUT_MS = 20_000

async function initReader() {
  if (!epubMount.value) return
  loading.value = true
  errorMsg.value = ''

  try {
    book = ePub(props.url)

    rendition = book.renderTo(epubMount.value, {
      width:  '100%',
      height: '100%',
      spread: 'none',
      flow:   'paginated',
    })

    applyTheme()

    rendition.on('relocated', loc => {
      lastLoc = loc

      if (loc.start?.index !== undefined) {
        currentPage.value = (loc.start.index ?? 0) + 1
      }

      let pct = null
      try {
        if (book?.locations?.length()) {
          const raw = book.locations.percentageFromCfi(loc.start.cfi)
          if (typeof raw === 'number' && !isNaN(raw)) {
            pct = Math.round(raw * 100)
            progress.value = pct
          }
        }
      } catch (_) {}

      if (props.ebookId && loc.start?.cfi) {
        scheduleProgressSave(loc.start.cfi, pct)
      }
    })

    let startCfi = null
    if (props.ebookId) {
      try {
        const r = await fetch(`/api/ebooks/${props.ebookId}/progress`)
        if (r.ok) {
          const p = await r.json()
          if (p.cfi) startCfi = p.cfi
        }
      } catch (_) {}
    }

    const timeout = new Promise((_, reject) =>
      setTimeout(() => reject(new Error('Tempo limite excedido ao carregar o livro.')), LOAD_TIMEOUT_MS)
    )
    await Promise.race([rendition.display(startCfi ?? undefined), timeout])

    loading.value = false

    book.ready.then(async () => {
      const meta = book.packaging?.metadata
      title.value = meta?.title || props.bookTitle || 'Livro'

      const nav = await book.navigation
      toc.value = flattenToc(nav?.toc || [])

      try {
        const spineLen = book.spine?.items?.length ?? 0
        if (spineLen > 0) totalPages.value = spineLen
      } catch (_) {}

      book.locations.generate(1024).then(() => {
        if (!lastLoc?.start?.cfi) return
        try {
          const raw = book.locations.percentageFromCfi(lastLoc.start.cfi)
          if (typeof raw === 'number' && !isNaN(raw)) {
            const pct = Math.round(raw * 100)
            progress.value = pct
            const total = book.locations.length()
            if (total > 0) totalPages.value = total
            if (lastLoc.start?.index !== undefined) {
              currentPage.value = (lastLoc.start.index ?? 0) + 1
            }
            if (props.ebookId) saveProgress(lastLoc.start.cfi, pct)
          }
        } catch (_) {}
      }).catch(() => {})
    }).catch(err => console.warn('book.ready error:', err))

  } catch (err) {
    console.error('epubjs error:', err)
    loading.value = false
    errorMsg.value = err?.message || 'Erro desconhecido ao abrir o arquivo EPUB.'
  }
}

function scheduleProgressSave(cfi, pct) {
  clearTimeout(saveTimer)
  saveTimer = setTimeout(() => saveProgress(cfi, pct ?? progress.value), 2000)
}

function saveProgress(cfi, percentage) {
  if (!props.ebookId) return
  fetch(`/api/ebooks/${props.ebookId}/progress`, {
    method:  'PUT',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify({ cfi, percentage: percentage ?? 0 }),
  }).catch(() => {})
}

// ── Page flip animation ───────────────────────────────────────────
async function flipPage(direction) {
  if (navigating.value || !rendition) return
  navigating.value = true

  flipDir.value     = direction === 'next' ? 'flip-next' : 'flip-prev'
  flipping.value    = true
  flipTurning.value = false

  // Let the flip card mount, then start the turn
  await nextTick()
  await wait(16)
  flipTurning.value = true

  // Halfway through the flip: navigate while card is edge-on (invisible)
  await wait(FLIP_MS / 2)
  try {
    if (direction === 'next') await rendition.next()
    else                      await rendition.prev()
  } catch (_) {}

  // Wait for the second half to complete
  await wait(FLIP_MS / 2)

  flipping.value    = false
  flipTurning.value = false
  navigating.value  = false
}

async function nextPage() { await flipPage('next') }
async function prevPage()  { await flipPage('prev') }

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
  if (e.key === 'Escape')                              emit('close')
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

/* ── Flip book container ─────────────────────── */
.flip-book {
  width: 100%;
  height: 100%;
  position: relative;
  perspective: 2000px;
}

/* ── Page layers ─────────────────────────────── */
.page-layer {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
}

.page-main {
  z-index: 1;
}

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

/* ── Flip card (the 3-D turning page) ────────── */
.flip-card {
  z-index: 10;
  transform-style: preserve-3d;
  backface-visibility: hidden;
}

/* Next: rotates around left edge (page peels left) */
.flip-card.flip-next {
  transform-origin: left center;
  transform: rotateY(0deg);
}
.flip-card.flip-next.flip-card--turning {
  transition: transform 0.5s cubic-bezier(0.645, 0.045, 0.355, 1.000);
  transform: rotateY(-180deg);
}

/* Prev: rotates around right edge (page peels right) */
.flip-card.flip-prev {
  transform-origin: right center;
  transform: rotateY(0deg);
}
.flip-card.flip-prev.flip-card--turning {
  transition: transform 0.5s cubic-bezier(0.645, 0.045, 0.355, 1.000);
  transform: rotateY(180deg);
}

/* ── Flip faces ──────────────────────────────── */
.flip-face {
  position: absolute;
  inset: 0;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  overflow: hidden;
}

.flip-face--front {
  transform: rotateY(0deg);
}

.flip-face--back {
  transform: rotateY(180deg);
}

/* Page background fill */
.page-bg {
  position: absolute;
  inset: 0;
  background: #fff;
}
.page-bg.dark {
  background: #1e1e2e;
}

/* Simulated text lines on the flip card faces */
.page-lines {
  position: absolute;
  inset: 40px 60px;
  background-image:
    repeating-linear-gradient(
      to bottom,
      transparent,
      transparent 24px,
      rgba(0,0,0,0.065) 24px,
      rgba(0,0,0,0.065) 25px
    );
}
.page-lines.dark {
  background-image:
    repeating-linear-gradient(
      to bottom,
      transparent,
      transparent 24px,
      rgba(255,255,255,0.06) 24px,
      rgba(255,255,255,0.06) 25px
    );
}

/* Edge shadow on front face (right side) */
.flip-edge-shadow--right {
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 28px;
  background: linear-gradient(to right, transparent, rgba(0,0,0,0.18));
  pointer-events: none;
}

/* Edge shadow on back face (left side, mirrored) */
.flip-edge-shadow--left {
  position: absolute;
  top: 0; left: 0; bottom: 0;
  width: 28px;
  background: linear-gradient(to left, transparent, rgba(0,0,0,0.18));
  pointer-events: none;
}

/* ── Cast shadow on the static page ─────────── */
.flip-cast-shadow {
  position: absolute;
  inset: 0;
  z-index: 5;
  pointer-events: none;
  opacity: 0;
  transition: opacity 0.5s ease;
}

.flip-cast-shadow.flip-next {
  background: linear-gradient(to right, rgba(0,0,0,0.22) 0%, transparent 60%);
}
.flip-cast-shadow.flip-prev {
  background: linear-gradient(to left, rgba(0,0,0,0.22) 0%, transparent 60%);
}

.flip-cast-shadow.flip-cast-shadow--spreading {
  opacity: 1;
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
  z-index: 30;
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

.footer-left {
  min-width: 90px;
}

.page-info {
  display: flex;
  align-items: baseline;
  gap: 3px;
  font-variant-numeric: tabular-nums;
}

.page-label {
  font-size: 0.65rem;
  color: #4b5563;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.page-num {
  font-size: 0.85rem;
  font-weight: 700;
  color: #818cf8;
  line-height: 1;
}

.page-total {
  font-size: 0.7rem;
  color: #4b5563;
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

.progress-pct {
  font-size: 0.7rem;
  color: #4b5563;
  min-width: 34px;
  text-align: right;
  font-variant-numeric: tabular-nums;
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

/* ── Cancel button (loading state) ───────────── */
.cancel-btn {
  margin-top: 4px;
  padding: 6px 18px;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 6px;
  background: transparent;
  color: #6b7280;
  font-size: 0.78rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.cancel-btn:hover { background: rgba(255,255,255,0.06); color: #d1d5db; }

/* ── Error state ─────────────────────────────── */
.err-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #f3f4f6;
  margin-top: 4px;
}
.err-msg {
  font-size: 0.78rem;
  color: #9ca3af;
  text-align: center;
  max-width: 320px;
  line-height: 1.5;
}
.err-actions {
  display: flex;
  gap: 10px;
  margin-top: 4px;
}
.err-btn {
  padding: 7px 18px;
  border-radius: 6px;
  border: 1px solid rgba(255,255,255,0.12);
  background: transparent;
  color: #9ca3af;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}
.err-btn:hover { background: rgba(255,255,255,0.06); color: #f3f4f6; }
.err-retry {
  background: rgba(99,102,241,0.15);
  border-color: rgba(99,102,241,0.4);
  color: #818cf8;
}
.err-retry:hover { background: rgba(99,102,241,0.28); color: #a5b4fc; }
</style>
