<template>
  <Teleport to="body">
    <Transition name="sched-fade">
      <div v-if="open" class="sched-overlay" @keydown.esc.stop="close" @mousedown.self="close">

        <div class="sched-panel">

          <!-- ── Header ─────────────────────────────────── -->
          <div class="sched-header">
            <div class="sched-header-left">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                <line x1="3" y1="10" x2="21" y2="10"/>
              </svg>
              <span>Agendador</span>
            </div>
            <div class="sched-header-right">
              <button class="hdr-btn" @click="openForm()" title="Nova tarefa">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                Nova tarefa
              </button>
              <button class="hdr-icon-btn" @click="close" title="Fechar">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
          </div>

          <!-- ── Notification banner ───────────────────── -->
          <div v-if="scheduler.notifPerm === 'denied'" class="notif-banner notif-denied">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            Notificações bloqueadas. Ative nas configurações do browser.
          </div>
          <div v-else-if="scheduler.notifPerm === 'default'" class="notif-banner notif-ask">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
            Permita notificações para receber alertas.
            <button @click="scheduler.requestPermission()">Permitir</button>
          </div>

          <!-- ── Content ────────────────────────────────── -->
          <div class="sched-body">

            <!-- Form view -->
            <Transition name="form-slide">
              <div v-if="showForm" class="sched-form-wrap">
                <div class="form-title">{{ editingId ? 'Editar tarefa' : 'Nova tarefa' }}</div>

                <div class="form-group">
                  <label>Título <span class="req">*</span></label>
                  <input v-model="form.title" class="f-input" placeholder="Nome do compromisso" maxlength="80" />
                </div>

                <div class="form-group">
                  <label>Descrição</label>
                  <textarea v-model="form.description" class="f-input f-textarea" placeholder="Detalhes (opcional)" rows="2" maxlength="300" />
                </div>

                <div class="form-row">
                  <div class="form-group">
                    <label>Data <span class="req">*</span></label>
                    <input v-model="form.date" type="date" class="f-input" :min="today" />
                  </div>
                  <div class="form-group">
                    <label>Hora <span class="req">*</span></label>
                    <input v-model="form.time" type="time" class="f-input" />
                  </div>
                </div>

                <div class="form-group">
                  <label>Repetição</label>
                  <select v-model="form.recurrence" class="f-input">
                    <option value="none">Não repetir</option>
                    <option value="daily">Diariamente</option>
                    <option value="weekdays">Dias úteis (Seg–Sex)</option>
                    <option value="weekly">Semanalmente</option>
                    <option value="monthly">Mensalmente</option>
                  </select>
                </div>

                <div class="form-group">
                  <label>Avisar antes</label>
                  <select v-model.number="form.notifyBefore" class="f-input">
                    <option :value="0">Exatamente na hora</option>
                    <option :value="5">5 minutos antes</option>
                    <option :value="10">10 minutos antes</option>
                    <option :value="15">15 minutos antes</option>
                    <option :value="30">30 minutos antes</option>
                  </select>
                </div>

                <div class="form-row form-row--align">
                  <div class="form-group form-group--inline">
                    <label>Som</label>
                    <button
                      class="toggle-btn"
                      :class="{ 'toggle-btn--on': form.soundEnabled }"
                      @click="form.soundEnabled = !form.soundEnabled"
                    >
                      <span class="toggle-knob"></span>
                    </button>
                  </div>

                  <div class="form-group" v-if="form.soundEnabled">
                    <label>Tipo de alarme</label>
                    <div class="sound-opts">
                      <button
                        v-for="s in SOUND_TYPES"
                        :key="s.value"
                        class="sound-opt"
                        :class="{ active: form.soundType === s.value }"
                        @click="selectSound(s.value)"
                        :title="s.label"
                      >{{ s.label }}</button>
                    </div>
                  </div>
                </div>

                <div class="form-error" v-if="formError">{{ formError }}</div>

                <div class="form-actions">
                  <button class="f-btn f-btn--cancel" @click="cancelForm">Cancelar</button>
                  <button class="f-btn f-btn--save" @click="submitForm">
                    {{ editingId ? 'Salvar' : 'Criar tarefa' }}
                  </button>
                </div>
              </div>
            </Transition>

            <!-- Task list view -->
            <div v-if="!showForm" class="task-list">

              <!-- Empty state -->
              <div v-if="scheduler.sortedTasks.length === 0" class="empty-state">
                <svg width="52" height="52" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" opacity="0.3">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
                <p>Nenhuma tarefa agendada.<br>Crie uma para começar.</p>
              </div>

              <!-- Task cards -->
              <div
                v-for="task in scheduler.sortedTasks"
                :key="task.id"
                class="task-card"
                :class="{
                  'task-card--disabled': !task.enabled,
                  'task-card--overdue':   task.enabled && isOverdue(task),
                }"
              >
                <div class="task-card-top">
                  <div class="task-info">
                    <div class="task-title">{{ task.title }}</div>
                    <div class="task-desc" v-if="task.description">{{ task.description }}</div>
                  </div>
                  <div class="task-actions">
                    <button class="act-btn" @click="scheduler.toggleTask(task.id)" :title="task.enabled ? 'Desativar' : 'Ativar'">
                      <svg v-if="task.enabled" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18.36 6.64A9 9 0 0 1 21 12a9 9 0 0 1-9 9 9 9 0 0 1-9-9 9 9 0 0 1 2.64-6.36"/><line x1="12" y1="2" x2="12" y2="12"/></svg>
                      <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" opacity="0.4"><path d="M18.36 6.64A9 9 0 0 1 21 12a9 9 0 0 1-9 9 9 9 0 0 1-9-9 9 9 0 0 1 2.64-6.36"/><line x1="12" y1="2" x2="12" y2="12"/></svg>
                    </button>
                    <button class="act-btn" @click="openForm(task)" title="Editar">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
                    </button>
                    <button class="act-btn act-btn--del" @click="confirmDelete(task)" title="Excluir">
                      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg>
                    </button>
                  </div>
                </div>

                <div class="task-meta">
                  <span class="task-datetime">{{ fmtDatetime(task.datetime) }}</span>
                  <span v-if="task.notifyBefore > 0" class="task-badge badge-notify">{{ task.notifyBefore }} min antes</span>
                  <span v-if="task.recurrence !== 'none'" class="task-badge badge-recur">{{ RECUR_LABELS[task.recurrence] }}</span>
                  <span v-if="!task.enabled" class="task-badge badge-off">Desativado</span>
                </div>

                <div class="task-countdown" :class="{ 'countdown--overdue': isOverdue(task) }" v-if="task.enabled">
                  {{ timeUntil(task) }}
                </div>
              </div>
            </div>

          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useSchedulerStore } from '../store/scheduler.js'
import { useAlarmSound } from '../composables/useAlarmSound.js'

const props  = defineProps({ open: Boolean })
const emit   = defineEmits(['update:open'])
const close  = () => emit('update:open', false)

const scheduler = useSchedulerStore()

const SOUND_TYPES = [
  { value: 'gentle',  label: 'Suave'   },
  { value: 'default', label: 'Padrão'  },
  { value: 'urgent',  label: 'Urgente' },
]
const RECUR_LABELS = {
  daily:    'Diário',
  weekdays: 'Dias úteis',
  weekly:   'Semanal',
  monthly:  'Mensal',
}

// ── Form state ─────────────────────────────────────────────────────
const showForm  = ref(false)
const editingId = ref(null)
const formError = ref('')

const blankForm = () => ({
  title:        '',
  description:  '',
  date:         '',
  time:         '',
  recurrence:   'none',
  notifyBefore: 0,
  soundEnabled: true,
  soundType:    'default',
})
const form = ref(blankForm())

const today = computed(() => new Date().toISOString().slice(0, 10))

function openForm(task = null) {
  formError.value = ''
  if (task) {
    const d = new Date(task.datetime)
    editingId.value = task.id
    form.value = {
      title:        task.title,
      description:  task.description,
      date:         d.toISOString().slice(0, 10),
      time:         task.time,
      recurrence:   task.recurrence,
      notifyBefore: task.notifyBefore,
      soundEnabled: task.soundEnabled,
      soundType:    task.soundType,
    }
  } else {
    editingId.value = null
    form.value = blankForm()
    // Default to next round hour
    const now = new Date()
    now.setHours(now.getHours() + 1, 0, 0, 0)
    form.value.date = now.toISOString().slice(0, 10)
    form.value.time = `${String(now.getHours()).padStart(2,'0')}:${String(now.getMinutes()).padStart(2,'0')}`
  }
  showForm.value = true
}

function cancelForm() {
  showForm.value = false
  editingId.value = null
  formError.value = ''
}

const previewSound = useAlarmSound()
function selectSound(type) {
  form.value.soundType = type
  previewSound.stop()
  previewSound.play(type)
  setTimeout(previewSound.stop, 3000)
}

function submitForm() {
  formError.value = ''
  if (!form.value.title.trim()) { formError.value = 'Informe o título da tarefa.'; return }
  if (!form.value.date)         { formError.value = 'Informe a data.'; return }
  if (!form.value.time)         { formError.value = 'Informe o horário.'; return }

  const datetime = new Date(`${form.value.date}T${form.value.time}:00`)
  if (isNaN(datetime)) { formError.value = 'Data ou hora inválida.'; return }

  const payload = {
    title:        form.value.title.trim(),
    description:  form.value.description.trim(),
    datetime:     datetime.toISOString(),
    time:         form.value.time,
    recurrence:   form.value.recurrence,
    notifyBefore: form.value.notifyBefore,
    soundEnabled: form.value.soundEnabled,
    soundType:    form.value.soundType,
  }

  if (editingId.value) {
    scheduler.updateTask(editingId.value, payload)
  } else {
    scheduler.addTask(payload)
  }

  cancelForm()
}

function confirmDelete(task) {
  if (confirm(`Excluir "${task.title}"?`)) scheduler.deleteTask(task.id)
}

// ── Time display ───────────────────────────────────────────────────
function fmtDatetime(iso) {
  return new Date(iso).toLocaleString('pt-BR', {
    weekday: 'short', day: '2-digit', month: 'short',
    hour: '2-digit', minute: '2-digit',
  })
}

function isOverdue(task) {
  return new Date(task.datetime) < new Date()
}

function timeUntil(task) {
  const diff = new Date(task.datetime) - now.value
  if (diff < 0) return 'Vencida'
  const mins  = Math.floor(diff / 60_000)
  const hours = Math.floor(mins / 60)
  const days  = Math.floor(hours / 24)
  if (days  > 0) return `em ${days}d ${hours % 24}h`
  if (hours > 0) return `em ${hours}h ${mins % 60}min`
  if (mins  > 0) return `em ${mins} min`
  return 'Agora!'
}

// Live countdown ticker
const now = ref(new Date())
let ticker = null
onMounted(() => { ticker = setInterval(() => { now.value = new Date() }, 30_000) })
onUnmounted(() => { clearInterval(ticker); previewSound.stop() })
</script>

<style scoped>
/* ── Overlay ────────────────────────────────────── */
.sched-overlay {
  position: fixed;
  inset: 0;
  z-index: 9000;
  display: flex;
  align-items: stretch;
  justify-content: flex-end;
  background: rgba(0,0,0,0.45);
  backdrop-filter: blur(3px);
}

/* ── Panel ──────────────────────────────────────── */
.sched-panel {
  width: min(420px, 100vw);
  background: #0f172a;
  border-left: 1px solid rgba(255,255,255,0.06);
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}

/* ── Header ─────────────────────────────────────── */
.sched-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.06);
  flex-shrink: 0;
}
.sched-header-left {
  display: flex; align-items: center; gap: 8px;
  font-weight: 600; font-size: 0.92rem; color: #e2e8f0;
}
.sched-header-right { display: flex; align-items: center; gap: 6px; }

.hdr-btn {
  display: flex; align-items: center; gap: 5px;
  padding: 6px 12px;
  border-radius: 8px;
  border: 1px solid rgba(99,102,241,0.4);
  background: rgba(99,102,241,0.12);
  color: #818cf8;
  font-size: 0.78rem; font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.hdr-btn:hover { background: rgba(99,102,241,0.25); }

.hdr-icon-btn {
  width: 32px; height: 32px;
  border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);
  background: transparent; color: #64748b;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background 0.15s, color 0.15s;
}
.hdr-icon-btn:hover { background: rgba(255,255,255,0.06); color: #e2e8f0; }

/* ── Notification banners ───────────────────────── */
.notif-banner {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 14px; font-size: 0.76rem; flex-shrink: 0;
}
.notif-denied { background: rgba(239,68,68,0.08); color: #f87171; border-bottom: 1px solid rgba(239,68,68,0.15); }
.notif-ask    { background: rgba(234,179,8,0.08);  color: #fbbf24; border-bottom: 1px solid rgba(234,179,8,0.15); }
.notif-ask button {
  margin-left: auto; padding: 3px 10px; border-radius: 5px;
  border: 1px solid rgba(234,179,8,0.4); background: rgba(234,179,8,0.1);
  color: #fbbf24; font-size: 0.74rem; cursor: pointer;
}
.notif-ask button:hover { background: rgba(234,179,8,0.2); }

/* ── Body ───────────────────────────────────────── */
.sched-body {
  flex: 1; overflow-y: auto; overflow-x: hidden; position: relative;
}
.sched-body::-webkit-scrollbar { width: 4px; }
.sched-body::-webkit-scrollbar-track { background: transparent; }
.sched-body::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 2px; }

/* ── Form ───────────────────────────────────────── */
.sched-form-wrap {
  padding: 20px 16px;
  display: flex; flex-direction: column; gap: 14px;
}
.form-title {
  font-size: 0.95rem; font-weight: 700; color: #e2e8f0; margin-bottom: 2px;
}
.form-group {
  display: flex; flex-direction: column; gap: 5px;
}
.form-group label {
  font-size: 0.72rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.06em; color: #64748b;
}
.req { color: #f87171; }

.form-row {
  display: grid; grid-template-columns: 1fr 1fr; gap: 10px;
}
.form-row--align { align-items: flex-start; }
.form-group--inline {
  flex-direction: row; align-items: center; gap: 10px;
}
.form-group--inline label { margin: 0; }

.f-input {
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: 8px;
  padding: 8px 10px;
  color: #e2e8f0;
  font-size: 0.85rem;
  transition: border-color 0.15s;
  width: 100%;
  box-sizing: border-box;
}
.f-input:focus { outline: none; border-color: rgba(99,102,241,0.5); }
.f-textarea { resize: vertical; min-height: 56px; font-family: inherit; }

/* ── Toggle ─────────────────────────────────────── */
.toggle-btn {
  width: 42px; height: 24px;
  border-radius: 12px; border: none;
  background: rgba(255,255,255,0.1);
  cursor: pointer; position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}
.toggle-btn--on { background: #6366f1; }
.toggle-knob {
  position: absolute; top: 3px; left: 3px;
  width: 18px; height: 18px;
  border-radius: 50%; background: #fff;
  transition: transform 0.2s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.3);
}
.toggle-btn--on .toggle-knob { transform: translateX(18px); }

/* ── Sound options ───────────────────────────────── */
.sound-opts {
  display: flex; gap: 6px;
}
.sound-opt {
  flex: 1; padding: 6px 0;
  border-radius: 6px; border: 1px solid rgba(255,255,255,0.08);
  background: transparent; color: #64748b;
  font-size: 0.74rem; cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.sound-opt.active {
  background: rgba(99,102,241,0.15);
  border-color: rgba(99,102,241,0.4);
  color: #a5b4fc;
}
.sound-opt:hover:not(.active) { background: rgba(255,255,255,0.04); color: #94a3b8; }

/* ── Form error / actions ────────────────────────── */
.form-error {
  font-size: 0.78rem; color: #f87171;
  padding: 8px 12px; border-radius: 6px;
  background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2);
}
.form-actions {
  display: flex; gap: 8px; margin-top: 4px;
}
.f-btn {
  flex: 1; padding: 10px;
  border-radius: 8px; border: none;
  font-size: 0.85rem; font-weight: 600; cursor: pointer;
  transition: background 0.15s;
}
.f-btn--cancel {
  background: rgba(255,255,255,0.06); color: #64748b;
  border: 1px solid rgba(255,255,255,0.08);
}
.f-btn--cancel:hover { background: rgba(255,255,255,0.1); color: #94a3b8; }
.f-btn--save { background: #6366f1; color: #fff; }
.f-btn--save:hover { background: #4f46e5; }

/* ── Form slide transition ───────────────────────── */
.form-slide-enter-active { animation: slide-in 0.25s ease; }
.form-slide-leave-active { animation: slide-in 0.2s ease reverse; }
@keyframes slide-in { from { opacity: 0; transform: translateX(24px); } to { opacity: 1; transform: none; } }

/* ── Task list ───────────────────────────────────── */
.task-list { padding: 12px 12px 24px; display: flex; flex-direction: column; gap: 8px; }

.empty-state {
  display: flex; flex-direction: column; align-items: center; gap: 10px;
  padding: 60px 0; color: #334155; text-align: center;
}
.empty-state p { font-size: 0.85rem; line-height: 1.6; margin: 0; }

/* ── Task card ───────────────────────────────────── */
.task-card {
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.07);
  border-radius: 10px;
  padding: 12px 14px;
  transition: border-color 0.2s;
}
.task-card:hover { border-color: rgba(99,102,241,0.25); }
.task-card--disabled { opacity: 0.45; }
.task-card--overdue  { border-color: rgba(239,68,68,0.3); }

.task-card-top {
  display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;
}
.task-info { flex: 1; min-width: 0; }
.task-title {
  font-size: 0.9rem; font-weight: 600; color: #e2e8f0;
  white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.task-desc {
  font-size: 0.76rem; color: #64748b;
  margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}

.task-actions { display: flex; gap: 4px; flex-shrink: 0; }
.act-btn {
  width: 28px; height: 28px;
  border-radius: 6px; border: none;
  background: transparent; color: #475569;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; transition: background 0.15s, color 0.15s;
}
.act-btn:hover { background: rgba(255,255,255,0.07); color: #94a3b8; }
.act-btn--del:hover { background: rgba(239,68,68,0.1); color: #f87171; }

.task-meta {
  display: flex; flex-wrap: wrap; align-items: center; gap: 6px;
  margin-top: 8px;
}
.task-datetime { font-size: 0.75rem; color: #64748b; }

.task-badge {
  font-size: 0.65rem; font-weight: 600; padding: 2px 7px;
  border-radius: 20px; letter-spacing: 0.04em;
}
.badge-recur  { background: rgba(99,102,241,0.12); color: #818cf8; }
.badge-notify { background: rgba(234,179,8,0.1);   color: #f59e0b; }
.badge-off    { background: rgba(255,255,255,0.06); color: #475569; }

.task-countdown {
  margin-top: 6px;
  font-size: 0.72rem; font-weight: 600;
  color: #22c55e;
}
.countdown--overdue { color: #f87171; }

/* ── Panel transition ────────────────────────────── */
.sched-fade-enter-active .sched-panel,
.sched-fade-leave-active .sched-panel { transition: transform 0.28s cubic-bezier(0.4,0,0.2,1); }
.sched-fade-enter-from .sched-panel   { transform: translateX(100%); }
.sched-fade-leave-to   .sched-panel   { transform: translateX(100%); }
.sched-fade-enter-active, .sched-fade-leave-active { transition: background 0.28s; }
.sched-fade-enter-from, .sched-fade-leave-to { background: transparent; backdrop-filter: none; }
</style>
