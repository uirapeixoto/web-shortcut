<template>
  <Teleport to="body">
    <Transition name="kb-fade">
      <div v-if="open" class="kb-overlay" @keydown.esc.window="close">

        <!-- Board panel -->
        <div class="kb-panel" :class="{ 'kb-panel--fs': fullscreen }">

          <!-- Toolbar -->
          <div class="kb-toolbar">
            <div class="kb-toolbar-left">
              <svg class="kb-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="5" height="18" rx="1"/><rect x="10" y="3" width="5" height="11" rx="1"/><rect x="17" y="3" width="5" height="14" rx="1"/></svg>
              <span v-if="!editingBoardTitle" class="kb-board-title" @dblclick="startEditBoard">{{ boardTitle }}</span>
              <input v-else ref="boardTitleInput" v-model="boardTitle" class="kb-board-title-input"
                @blur="editingBoardTitle = false" @keydown.enter="editingBoardTitle = false" @keydown.esc="editingBoardTitle = false" />
            </div>

            <div class="kb-toolbar-right">
              <button class="kb-tool-btn" title="Adicionar coluna" @click="addColumn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="5" height="18" rx="1"/><line x1="20" y1="9" x2="20" y2="15"/><line x1="17" y1="12" x2="23" y2="12"/></svg>
                <span>Coluna</span>
              </button>
              <button class="kb-tool-btn" :title="fullscreen ? 'Restaurar' : 'Tela cheia'" @click="fullscreen = !fullscreen">
                <svg v-if="!fullscreen" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>
                <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="10" y1="14" x2="3" y2="21"/><line x1="21" y1="3" x2="14" y2="10"/></svg>
              </button>
              <button class="kb-tool-btn kb-tool-close" title="Fechar (Esc)" @click="close">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
          </div>

          <!-- Board -->
          <div class="kb-board" @click.self="cancelInlineAdd">
            <div
              v-for="col in data.columns"
              :key="col.id"
              class="kb-column"
              :class="{ 'kb-column--over': dragOver === col.id }"
              @dragover.prevent="dragOver = col.id"
              @dragleave="onColDragLeave(col.id)"
              @drop.prevent="onDrop(col.id, null)"
            >
              <!-- Column header -->
              <div class="kb-col-header" :style="{ '--col-accent': col.color }">
                <div class="kb-col-color-bar" :style="{ background: col.color }"></div>
                <input
                  v-if="col.editingTitle"
                  :ref="el => colInputs[col.id] = el"
                  v-model="col.title"
                  class="kb-col-title-input"
                  @blur="col.editingTitle = false"
                  @keydown.enter="col.editingTitle = false"
                  @keydown.esc="col.editingTitle = false"
                />
                <span v-else class="kb-col-title" @dblclick="startEditColTitle(col)">{{ col.title }}</span>
                <span class="kb-col-count">{{ (data.cards[col.id] || []).length }}</span>
                <div class="kb-col-menu">
                  <button class="kb-icon-btn" title="Cor da coluna" @click.stop="openColColorPicker(col)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M4.22 4.22l2.12 2.12M17.66 17.66l2.12 2.12M2 12h3M19 12h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/></svg>
                  </button>
                  <button class="kb-icon-btn" title="Excluir coluna" @click.stop="deleteColumn(col.id)">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/></svg>
                  </button>
                </div>
              </div>

              <!-- Color picker popover -->
              <div v-if="colColorPicker === col.id" class="kb-color-picker">
                <button v-for="c in CARD_COLORS" :key="c" class="kb-color-swatch"
                  :style="{ background: c }" :class="{ selected: col.color === c }"
                  @click="col.color = c; colColorPicker = null; save()" />
              </div>

              <!-- Cards -->
              <div class="kb-cards">
                <div
                  v-for="(card, idx) in (data.cards[col.id] || [])"
                  :key="card.id"
                  class="kb-card"
                  :class="{ 'kb-card--dragging': dragging?.id === card.id, 'kb-card--drop-before': dropTarget?.colId === col.id && dropTarget?.idx === idx }"
                  draggable="true"
                  @dragstart="onDragStart(card, col.id, idx)"
                  @dragend="onDragEnd"
                  @dragover.prevent.stop="onCardDragOver(col.id, idx)"
                  @drop.prevent.stop="onDrop(col.id, idx)"
                  @click="openCard(card, col.id)"
                >
                  <div v-if="card.color" class="kb-card-stripe" :style="{ background: card.color }"></div>
                  <div class="kb-card-body">
                    <div class="kb-card-labels" v-if="card.labels?.length">
                      <span v-for="l in card.labels" :key="l.text" class="kb-label" :style="{ background: l.color }">{{ l.text }}</span>
                    </div>
                    <p class="kb-card-title">{{ card.title }}</p>
                    <p v-if="card.desc" class="kb-card-desc">{{ card.desc }}</p>
                    <div class="kb-card-meta">
                      <span v-if="card.checklist?.length" class="kb-meta-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
                        {{ card.checklist.filter(i => i.done).length }}/{{ card.checklist.length }}
                      </span>
                    </div>
                  </div>
                </div>

                <!-- Drop zone at end of list -->
                <div
                  class="kb-drop-end"
                  :class="{ 'kb-drop-end--active': dragOver === col.id && dropTarget?.colId !== col.id }"
                  @dragover.prevent="dragOver = col.id; dropTarget = { colId: col.id, idx: (data.cards[col.id]||[]).length }"
                  @drop.prevent="onDrop(col.id, (data.cards[col.id]||[]).length)"
                ></div>
              </div>

              <!-- Inline add card -->
              <div v-if="inlineAdd === col.id" class="kb-inline-add">
                <textarea
                  ref="inlineTextarea"
                  v-model="inlineText"
                  class="kb-inline-textarea"
                  placeholder="Título do cartão..."
                  rows="2"
                  @keydown.enter.prevent="confirmInlineAdd(col.id)"
                  @keydown.esc="cancelInlineAdd"
                />
                <div class="kb-inline-actions">
                  <button class="kb-inline-confirm" @click="confirmInlineAdd(col.id)">Adicionar</button>
                  <button class="kb-inline-cancel" @click="cancelInlineAdd">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
              </div>
              <button v-else class="kb-add-card-btn" @click.stop="startInlineAdd(col.id)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Adicionar cartão
              </button>
            </div>

            <!-- Add column -->
            <div class="kb-add-col-wrap">
              <div v-if="addingCol" class="kb-add-col-form">
                <input ref="addColInput" v-model="newColTitle" class="kb-add-col-input"
                  placeholder="Nome da coluna..."
                  @keydown.enter="confirmAddColumn"
                  @keydown.esc="addingCol = false" />
                <div class="kb-inline-actions">
                  <button class="kb-inline-confirm" @click="confirmAddColumn">Criar</button>
                  <button class="kb-inline-cancel" @click="addingCol = false">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                  </button>
                </div>
              </div>
              <button v-else class="kb-add-col-btn" @click="addColumn">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Adicionar coluna
              </button>
            </div>
          </div>
        </div>

        <!-- Card detail modal -->
        <Transition name="kb-modal">
          <div v-if="activeCard" class="kb-modal-overlay" @click.self="closeCard">
            <div class="kb-card-modal">
              <div class="kb-modal-header">
                <div class="kb-modal-color-row">
                  <button v-for="c in CARD_COLORS" :key="c" class="kb-color-swatch sm"
                    :style="{ background: c }" :class="{ selected: activeCard.color === c }"
                    @click="activeCard.color = c; save()" />
                  <button class="kb-color-swatch sm clear" @click="activeCard.color = null; save()" title="Sem cor">✕</button>
                </div>
                <button class="kb-icon-btn" @click="closeCard">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
              </div>

              <div v-if="activeCard.color" class="kb-modal-stripe" :style="{ background: activeCard.color }"></div>

              <div class="kb-modal-body">
                <input v-model="activeCard.title" class="kb-modal-title" placeholder="Título do cartão" @change="save" />

                <!-- Labels -->
                <div class="kb-modal-section">
                  <span class="kb-modal-label-head">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z"/><line x1="7" y1="7" x2="7.01" y2="7"/></svg>
                    Etiquetas
                  </span>
                  <div class="kb-labels-editor">
                    <div v-for="(lbl, li) in activeCard.labels" :key="li" class="kb-lbl-row">
                      <span class="kb-label" :style="{ background: lbl.color }">{{ lbl.text }}</span>
                      <button class="kb-icon-btn sm" @click="activeCard.labels.splice(li, 1); save()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      </button>
                    </div>
                    <div class="kb-lbl-add-row">
                      <input v-model="newLabelText" placeholder="Nova etiqueta..." class="kb-lbl-input" @keydown.enter="addLabel" />
                      <div class="kb-lbl-colors">
                        <button v-for="c in LABEL_COLORS" :key="c" class="kb-color-swatch xs" :style="{ background: c }"
                          :class="{ selected: newLabelColor === c }" @click="newLabelColor = c" />
                      </div>
                      <button class="kb-inline-confirm sm" @click="addLabel">+</button>
                    </div>
                  </div>
                </div>

                <!-- Description -->
                <div class="kb-modal-section">
                  <span class="kb-modal-label-head">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg>
                    Descrição
                  </span>
                  <textarea v-model="activeCard.desc" class="kb-modal-desc" placeholder="Adicione uma descrição..." rows="3" @change="save" />
                </div>

                <!-- Checklist -->
                <div class="kb-modal-section">
                  <span class="kb-modal-label-head">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="9 11 12 14 22 4"/><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/></svg>
                    Checklist
                    <span v-if="activeCard.checklist?.length" class="kb-check-progress">
                      {{ Math.round(activeCard.checklist.filter(i=>i.done).length / activeCard.checklist.length * 100) }}%
                    </span>
                  </span>
                  <div v-if="activeCard.checklist?.length" class="kb-progress-bar">
                    <div class="kb-progress-fill" :style="{ width: (activeCard.checklist.filter(i=>i.done).length / activeCard.checklist.length * 100) + '%' }"></div>
                  </div>
                  <div class="kb-checklist">
                    <label v-for="(item, ii) in (activeCard.checklist || [])" :key="ii" class="kb-check-item">
                      <input type="checkbox" v-model="item.done" @change="save" />
                      <span :class="{ done: item.done }">{{ item.text }}</span>
                      <button class="kb-icon-btn sm" @click="activeCard.checklist.splice(ii, 1); save()">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                      </button>
                    </label>
                  </div>
                  <div class="kb-check-add">
                    <input v-model="newCheckItem" placeholder="Novo item..." class="kb-lbl-input"
                      @keydown.enter="addCheckItem" />
                    <button class="kb-inline-confirm sm" @click="addCheckItem">+</button>
                  </div>
                </div>
              </div>

              <div class="kb-modal-footer">
                <span class="kb-modal-col-badge">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="5" height="18" rx="1"/></svg>
                  {{ getColName(activeCard._colId) }}
                </span>
                <button class="kb-delete-btn" @click="deleteCard">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/></svg>
                  Excluir cartão
                </button>
              </div>
            </div>
          </div>
        </Transition>

      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, nextTick, watch, onMounted, onUnmounted } from 'vue'

const props = defineProps({ open: Boolean })
const emit = defineEmits(['update:open'])

const STORAGE_KEY = 'kanban-data'
const BOARD_TITLE_KEY = 'kanban-board-title'

const CARD_COLORS = ['#6366f1', '#a855f7', '#ec4899', '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4', '#3b82f6', null]
const LABEL_COLORS = ['#6366f1', '#a855f7', '#ec4899', '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4']

const uid = () => Math.random().toString(36).slice(2, 9)

const defaultData = () => ({
  columns: [
    { id: uid(), title: 'A Fazer', color: '#6366f1', editingTitle: false },
    { id: uid(), title: 'Em Progresso', color: '#f97316', editingTitle: false },
    { id: uid(), title: 'Revisão', color: '#a855f7', editingTitle: false },
    { id: uid(), title: 'Concluído', color: '#22c55e', editingTitle: false },
  ],
  cards: {}
})

function loadData() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    // ensure editingTitle exists
    parsed.columns.forEach(c => { c.editingTitle = false })
    return parsed
  } catch { return null }
}

const data = ref(loadData() || defaultData())

// ensure cards map has entries for all columns
data.value.columns.forEach(c => {
  if (!data.value.cards[c.id]) data.value.cards[c.id] = []
})

// seed demo cards if empty
if (data.value.columns.length && Object.values(data.value.cards).every(a => a.length === 0)) {
  const [c1, c2, , c4] = data.value.columns
  data.value.cards[c1.id] = [
    { id: uid(), title: 'Criar layout da homepage', desc: '', color: '#6366f1', labels: [{ text: 'design', color: '#a855f7' }], checklist: [] },
    { id: uid(), title: 'Configurar autenticação JWT', desc: 'Implementar refresh tokens e revogação.', color: null, labels: [{ text: 'backend', color: '#06b6d4' }], checklist: [{ text: 'Access token', done: true }, { text: 'Refresh token', done: false }] },
    { id: uid(), title: 'Escrever testes unitários', desc: '', color: null, labels: [], checklist: [] },
  ]
  data.value.cards[c2.id] = [
    { id: uid(), title: 'API de categorias', desc: 'CRUD completo com paginação.', color: '#f97316', labels: [{ text: 'backend', color: '#06b6d4' }], checklist: [] },
    { id: uid(), title: 'Componente ShortcutCard', desc: '', color: null, labels: [{ text: 'frontend', color: '#ec4899' }], checklist: [] },
  ]
  data.value.cards[c4.id] = [
    { id: uid(), title: 'Setup do projeto Vue + Vite', desc: '', color: null, labels: [], checklist: [] },
  ]
  save()
}

const boardTitle = ref(localStorage.getItem(BOARD_TITLE_KEY) || 'Meu Quadro')
const editingBoardTitle = ref(false)
const boardTitleInput = ref(null)
const fullscreen = ref(false)
const colInputs = ref({})

// drag state
const dragging = ref(null) // { id, colId, idx }
const dragOver = ref(null)  // colId being hovered
const dropTarget = ref(null) // { colId, idx }

// inline add card
const inlineAdd = ref(null) // colId
const inlineText = ref('')
const inlineTextarea = ref(null)

// add column
const addingCol = ref(false)
const newColTitle = ref('')
const addColInput = ref(null)

// col color picker
const colColorPicker = ref(null)

// card detail
const activeCard = ref(null)
const newCheckItem = ref('')
const newLabelText = ref('')
const newLabelColor = ref(LABEL_COLORS[0])

function save() {
  const plain = {
    columns: data.value.columns.map(({ id, title, color }) => ({ id, title, color })),
    cards: data.value.cards
  }
  localStorage.setItem(STORAGE_KEY, JSON.stringify(plain))
  localStorage.setItem(BOARD_TITLE_KEY, boardTitle.value)
}

watch(boardTitle, save)

function close() { emit('update:open', false) }

async function startEditBoard() {
  editingBoardTitle.value = true
  await nextTick()
  boardTitleInput.value?.select()
}

// ── Columns ──────────────────────────────────────────
function addColumn() {
  addingCol.value = true
  newColTitle.value = ''
  nextTick(() => addColInput.value?.focus())
}

function confirmAddColumn() {
  const title = newColTitle.value.trim()
  if (!title) { addingCol.value = false; return }
  const id = uid()
  const colors = ['#6366f1', '#a855f7', '#ec4899', '#ef4444', '#f97316', '#eab308', '#22c55e', '#06b6d4']
  const color = colors[data.value.columns.length % colors.length]
  data.value.columns.push({ id, title, color, editingTitle: false })
  data.value.cards[id] = []
  addingCol.value = false
  save()
}

function deleteColumn(colId) {
  if (!confirm('Excluir esta coluna e todos os seus cartões?')) return
  data.value.columns = data.value.columns.filter(c => c.id !== colId)
  delete data.value.cards[colId]
  save()
}

async function startEditColTitle(col) {
  col.editingTitle = true
  await nextTick()
  colInputs.value[col.id]?.select()
}

function openColColorPicker(col) {
  colColorPicker.value = colColorPicker.value === col.id ? null : col.id
}

// ── Cards ─────────────────────────────────────────────
async function startInlineAdd(colId) {
  cancelInlineAdd()
  inlineAdd.value = colId
  inlineText.value = ''
  await nextTick()
  // inlineTextarea is an array when using :ref in v-if
  const el = Array.isArray(inlineTextarea.value) ? inlineTextarea.value[0] : inlineTextarea.value
  el?.focus()
}

function confirmInlineAdd(colId) {
  const title = inlineText.value.trim()
  if (!title) { cancelInlineAdd(); return }
  if (!data.value.cards[colId]) data.value.cards[colId] = []
  data.value.cards[colId].push({ id: uid(), title, desc: '', color: null, labels: [], checklist: [] })
  inlineText.value = ''
  save()
  // keep the form open to allow quick successive adds
  nextTick(() => {
    const el = Array.isArray(inlineTextarea.value) ? inlineTextarea.value[0] : inlineTextarea.value
    el?.focus()
  })
}

function cancelInlineAdd() {
  inlineAdd.value = null
  inlineText.value = ''
  colColorPicker.value = null
}

function openCard(card, colId) {
  activeCard.value = { ...card, _colId: colId }
  newCheckItem.value = ''
  newLabelText.value = ''
}

function closeCard() {
  if (!activeCard.value) return
  // write back changes
  const colId = activeCard.value._colId
  const cards = data.value.cards[colId]
  if (cards) {
    const idx = cards.findIndex(c => c.id === activeCard.value.id)
    if (idx !== -1) {
      const { _colId, ...card } = activeCard.value
      cards[idx] = card
    }
  }
  save()
  activeCard.value = null
}

function deleteCard() {
  if (!confirm('Excluir este cartão?')) return
  const colId = activeCard.value._colId
  data.value.cards[colId] = (data.value.cards[colId] || []).filter(c => c.id !== activeCard.value.id)
  activeCard.value = null
  save()
}

function getColName(colId) {
  return data.value.columns.find(c => c.id === colId)?.title || ''
}

function addCheckItem() {
  const text = newCheckItem.value.trim()
  if (!text) return
  if (!activeCard.value.checklist) activeCard.value.checklist = []
  activeCard.value.checklist.push({ text, done: false })
  newCheckItem.value = ''
  save()
}

function addLabel() {
  const text = newLabelText.value.trim()
  if (!text) return
  if (!activeCard.value.labels) activeCard.value.labels = []
  activeCard.value.labels.push({ text, color: newLabelColor.value })
  newLabelText.value = ''
  save()
}

// ── Drag & Drop ───────────────────────────────────────
function onDragStart(card, colId, idx) {
  dragging.value = { id: card.id, colId, idx }
  dragOver.value = colId
}

function onDragEnd() {
  dragging.value = null
  dragOver.value = null
  dropTarget.value = null
}

function onCardDragOver(colId, idx) {
  dragOver.value = colId
  dropTarget.value = { colId, idx }
}

function onColDragLeave(colId) {
  if (dragOver.value === colId) {
    // only clear if not over a child
    setTimeout(() => {
      if (dragOver.value === colId) dragOver.value = null
    }, 50)
  }
}

function onDrop(toColId, toIdx) {
  if (!dragging.value) return
  const { id, colId: fromColId } = dragging.value
  const fromCards = data.value.cards[fromColId] || []
  const toCards = data.value.cards[toColId] || []
  const cardIdx = fromCards.findIndex(c => c.id === id)
  if (cardIdx === -1) return
  const [card] = fromCards.splice(cardIdx, 1)

  let insertAt = toIdx
  if (insertAt === null || insertAt === undefined) {
    insertAt = toCards.length
  }
  // adjust if dropping in same column after removal
  if (fromColId === toColId && cardIdx < insertAt) insertAt--
  if (insertAt < 0) insertAt = 0

  toCards.splice(insertAt, 0, card)
  data.value.cards[fromColId] = fromCards
  data.value.cards[toColId] = toCards
  dragging.value = null
  dragOver.value = null
  dropTarget.value = null
  save()
}

// ── Keyboard ──────────────────────────────────────────
function onKeydown(e) {
  if (e.key === 'Escape' && props.open && !activeCard.value) close()
}
onMounted(() => window.addEventListener('keydown', onKeydown))
onUnmounted(() => window.removeEventListener('keydown', onKeydown))
</script>
