<template>
  <!-- Full-screen reader mode -->
  <Teleport to="body">
    <Transition name="reader-fade">
      <div class="reader-portal" v-if="activeBook">
        <EpubFlipReader
          :url="`/api/ebooks/${activeBook.id}/book.epub`"
          :book-title="activeBook.title"
          :ebook-id="activeBook.id"
          @close="onCloseReader"
        />
      </div>
    </Transition>
  </Teleport>

  <!-- Library page -->
  <div class="ebooks-page">
    <div class="page-header">
      <h1 class="page-title">
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
        Biblioteca EPUB
      </h1>
      <p class="page-subtitle">Faça upload de arquivos .epub e leia com efeito de virar página</p>
    </div>

    <!-- Upload area -->
    <div
      class="upload-zone"
      :class="{ dragging: isDragging, uploading: isUploading }"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onDrop"
      @click="fileInput?.click()"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".epub"
        class="hidden-input"
        @change="onFileChange"
      />
      <div class="upload-icon">
        <svg v-if="!isUploading" width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
        <div v-else class="spin-icon"></div>
      </div>
      <div class="upload-text">
        <span v-if="isUploading">Enviando… {{ uploadProgress }}%</span>
        <span v-else-if="isDragging">Solte o arquivo aqui</span>
        <span v-else>Clique ou arraste um arquivo <strong>.epub</strong></span>
      </div>
      <div class="upload-sub" v-if="!isUploading">
        Os arquivos são salvos em <code>upload/ebook/epub/</code>
      </div>
      <div class="upload-progress-bar" v-if="isUploading">
        <div class="upload-progress-fill" :style="{ width: uploadProgress + '%' }"></div>
      </div>
    </div>

    <!-- Error message -->
    <Transition name="fade">
      <div class="error-bar" v-if="errorMsg">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
        {{ errorMsg }}
        <button @click="errorMsg = ''">×</button>
      </div>
    </Transition>

    <!-- Books grid -->
    <div class="section-title" v-if="books.length">
      <span>{{ books.length }} livro{{ books.length !== 1 ? 's' : '' }}</span>
    </div>

    <div class="books-grid" v-if="books.length">
      <div
        class="book-card"
        v-for="book in books"
        :key="book.id"
        @click="openBook(book)"
      >
        <div class="book-cover-art">
          <div class="book-spine-art"></div>
          <div class="book-pages-art"></div>
          <div class="book-cover-art-face">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" opacity="0.4"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
          </div>
          <div class="progress-overlay" v-if="progressMap[book.id]?.percentage > 0">
            <span class="progress-overlay-pct">{{ Math.round(progressMap[book.id].percentage) }}%</span>
            <span class="progress-overlay-label">lido</span>
            <div class="progress-overlay-bar">
              <div class="progress-overlay-fill" :style="{ width: progressMap[book.id].percentage + '%' }"></div>
            </div>
          </div>
        </div>
        <div class="book-info">
          <div class="book-title">{{ book.title }}</div>
          <div class="book-meta">
            <span>{{ formatSize(book.size) }}</span>
            <span>{{ formatDate(book.created_at) }}</span>
          </div>
        </div>
        <div class="book-actions" @click.stop>
          <button class="action-btn read-btn" @click="openBook(book)" title="Ler">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
            Ler
          </button>
          <button class="action-btn del-btn" @click="deleteBook(book)" title="Excluir">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Empty state -->
    <div class="empty-state" v-else-if="!isLoading">
      <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z"/></svg>
      <p>Nenhum livro ainda. Faça upload de um arquivo .epub!</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import EpubFlipReader from '../components/EpubFlipReader.vue'

const books       = ref([])
const activeBook  = ref(null)
const progressMap = ref({})
const fileInput   = ref(null)
const isDragging  = ref(false)
const isUploading = ref(false)
const uploadProgress = ref(0)
const isLoading   = ref(true)
const errorMsg    = ref('')

onMounted(async () => {
  await fetchBooks()
  await fetchProgress()
})

async function fetchBooks() {
  isLoading.value = true
  try {
    const r = await fetch('/api/ebooks/')
    books.value = await r.json()
  } catch {
    errorMsg.value = 'Erro ao carregar biblioteca'
  } finally {
    isLoading.value = false
  }
}

async function fetchProgress() {
  try {
    const r = await fetch('/api/ebooks/progress')
    if (r.ok) progressMap.value = await r.json()
  } catch (_) {}
}

function onCloseReader() {
  activeBook.value = null
  fetchProgress()
}

function onDrop(e) {
  isDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) uploadFile(file)
}

function onFileChange(e) {
  const file = e.target.files?.[0]
  if (file) uploadFile(file)
  if (fileInput.value) fileInput.value.value = ''
}

async function uploadFile(file) {
  if (!file.name.toLowerCase().endsWith('.epub')) {
    errorMsg.value = 'Apenas arquivos .epub são suportados'
    return
  }
  isUploading.value = true
  uploadProgress.value = 0
  errorMsg.value = ''

  const formData = new FormData()
  formData.append('file', file)

  try {
    const xhr = new XMLHttpRequest()
    await new Promise((resolve, reject) => {
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) uploadProgress.value = Math.round((e.loaded / e.total) * 100)
      }
      xhr.onload = () => {
        if (xhr.status >= 200 && xhr.status < 300) resolve(JSON.parse(xhr.responseText))
        else reject(new Error(xhr.responseText))
      }
      xhr.onerror = reject
      xhr.open('POST', '/api/ebooks/upload')
      xhr.send(formData)
    })
    await fetchBooks()
  } catch (err) {
    errorMsg.value = 'Erro ao enviar arquivo. Tente novamente.'
  } finally {
    isUploading.value = false
    uploadProgress.value = 0
  }
}

async function deleteBook(book) {
  if (!confirm(`Excluir "${book.title}"?`)) return
  try {
    await fetch(`/api/ebooks/${book.id}`, { method: 'DELETE' })
    books.value = books.value.filter(b => b.id !== book.id)
  } catch {
    errorMsg.value = 'Erro ao excluir livro'
  }
}

function openBook(book) {
  activeBook.value = book
}

function formatSize(bytes) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1048576) return `${(bytes / 1024).toFixed(0)} KB`
  return `${(bytes / 1048576).toFixed(1)} MB`
}

function formatDate(iso) {
  if (!iso) return ''
  try {
    return new Date(iso).toLocaleDateString('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' })
  } catch {
    return ''
  }
}
</script>

<style scoped>
/* ─── Reader portal ──────────────────────────── */
.reader-portal {
  position: fixed;
  inset: 0;
  z-index: 9999;
}
.reader-fade-enter-active, .reader-fade-leave-active { transition: opacity 0.3s; }
.reader-fade-enter-from, .reader-fade-leave-to { opacity: 0; }

/* ─── Page ───────────────────────────────────── */
.ebooks-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 32px 24px;
}

.page-header { margin-bottom: 28px; }
.page-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.5rem;
  font-weight: 700;
  margin: 0 0 6px;
}
.page-subtitle { color: var(--text-muted, #888); font-size: 0.9rem; margin: 0; }

/* ─── Upload zone ────────────────────────────── */
.upload-zone {
  border: 2px dashed rgba(99,102,241,0.4);
  border-radius: 14px;
  padding: 40px 24px;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
  position: relative;
  overflow: hidden;
  margin-bottom: 24px;
  background: rgba(99,102,241,0.03);
}
.upload-zone:hover,
.upload-zone.dragging {
  border-color: #6366f1;
  background: rgba(99,102,241,0.08);
}
.upload-zone.uploading { cursor: default; }
.hidden-input { display: none; }

.upload-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 12px;
  color: #6366f1;
}
.spin-icon {
  width: 36px; height: 36px;
  border: 3px solid rgba(99,102,241,0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.upload-text { font-size: 1rem; color: var(--text-main, #333); margin-bottom: 6px; }
.upload-sub { font-size: 0.8rem; color: #999; }
.upload-sub code { background: rgba(0,0,0,0.06); padding: 1px 5px; border-radius: 3px; font-size: 0.78rem; }

.upload-progress-bar {
  margin-top: 16px;
  height: 4px;
  background: rgba(99,102,241,0.15);
  border-radius: 2px;
  overflow: hidden;
}
.upload-progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  border-radius: 2px;
  transition: width 0.2s;
}

/* ─── Error bar ───────────────────────────────── */
.error-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  background: rgba(239,68,68,0.1);
  border: 1px solid rgba(239,68,68,0.3);
  border-radius: 8px;
  font-size: 0.85rem;
  color: #ef4444;
  margin-bottom: 20px;
}
.error-bar button {
  margin-left: auto;
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
}
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

/* ─── Section title ───────────────────────────── */
.section-title {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #999;
  margin-bottom: 16px;
}

/* ─── Books grid ─────────────────────────────── */
.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.book-card {
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.08);
  background: var(--card-bg, #fff);
  overflow: hidden;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}
.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0,0,0,0.12);
}

/* Book cover art */
.book-cover-art {
  height: 160px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}
.book-cover-art::before {
  content: '';
  position: absolute;
  inset: 0;
  background: repeating-linear-gradient(
    -45deg,
    rgba(255,255,255,0.03) 0px,
    rgba(255,255,255,0.03) 1px,
    transparent 1px,
    transparent 10px
  );
}
.book-spine-art {
  position: absolute;
  left: 0; top: 0; bottom: 0;
  width: 12px;
  background: rgba(0,0,0,0.25);
}
.book-pages-art {
  position: absolute;
  right: 0; top: 4px; bottom: 4px;
  width: 5px;
  background: repeating-linear-gradient(
    to bottom,
    #f5f5f5 0px,
    #f5f5f5 1px,
    #e0e0e0 1px,
    #e0e0e0 2px
  );
  border-radius: 0 2px 2px 0;
}
.book-cover-art-face {
  display: flex;
  align-items: center;
  justify-content: center;
  color: rgba(255,255,255,0.6);
}

/* Book info */
.book-info {
  padding: 12px 14px 8px;
  flex: 1;
}
.book-title {
  font-size: 0.88rem;
  font-weight: 600;
  margin-bottom: 4px;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}
.book-meta {
  display: flex;
  gap: 8px;
  font-size: 0.72rem;
  color: #999;
}

/* Book actions */
.book-actions {
  display: flex;
  gap: 6px;
  padding: 8px 12px 12px;
}
.action-btn {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 6px;
  border: none;
  font-size: 0.78rem;
  cursor: pointer;
  transition: background 0.15s;
}
.read-btn {
  flex: 1;
  justify-content: center;
  background: #6366f1;
  color: #fff;
}
.read-btn:hover { background: #4f46e5; }
.del-btn {
  background: rgba(239,68,68,0.1);
  color: #ef4444;
  padding: 5px 8px;
}
.del-btn:hover { background: rgba(239,68,68,0.2); }

/* ─── Empty state ────────────────────────────── */
.empty-state {
  text-align: center;
  padding: 60px 0;
  color: #bbb;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.empty-state p { font-size: 0.95rem; margin: 0; }

/* ─── Reading progress overlay ───────────────── */
.progress-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.52);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;
  backdrop-filter: blur(2px);
  border-radius: inherit;
}

.progress-overlay-pct {
  font-size: 2rem;
  font-weight: 800;
  color: #fff;
  line-height: 1;
  letter-spacing: -0.03em;
  text-shadow: 0 2px 8px rgba(0,0,0,0.4);
}

.progress-overlay-label {
  font-size: 0.62rem;
  color: rgba(255, 255, 255, 0.65);
  text-transform: uppercase;
  letter-spacing: 0.12em;
  font-weight: 600;
  margin-bottom: 10px;
}

.progress-overlay-bar {
  width: 60%;
  height: 3px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 2px;
  overflow: hidden;
  margin-top: 4px;
}

.progress-overlay-fill {
  height: 100%;
  background: #a5b4fc;
  border-radius: 2px;
  transition: width 0.3s;
}

/* ─── Dark mode ──────────────────────────────── */
@media (prefers-color-scheme: dark) {
  .book-card { background: #1e1e2e; border-color: rgba(255,255,255,0.06); }
  .upload-sub code { background: rgba(255,255,255,0.08); }
  .page-title, .page-subtitle { color: inherit; }
}
</style>
