import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

const STORAGE_KEY = 'ws_scheduled_tasks'
const CHECK_MS    = 30_000   // poll every 30 s
const FIRE_WIN_MS = 90_000   // catch alarms up to 90 s late (slow tab / sleep)

function uid() {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 7)
}

function calcNext(task, afterIso) {
  if (task.recurrence === 'none') return null
  const after = new Date(afterIso)
  const [h, m] = task.time.split(':').map(Number)
  const d = new Date(after)

  switch (task.recurrence) {
    case 'daily':
      d.setDate(d.getDate() + 1)
      break
    case 'weekdays':
      d.setDate(d.getDate() + 1)
      if (d.getDay() === 6) d.setDate(d.getDate() + 2) // Sat → Mon
      if (d.getDay() === 0) d.setDate(d.getDate() + 1) // Sun → Mon
      break
    case 'weekly':
      d.setDate(d.getDate() + 7)
      break
    case 'monthly':
      d.setMonth(d.getMonth() + 1)
      break
  }
  d.setHours(h, m, 0, 0)
  return d.toISOString()
}

export const useSchedulerStore = defineStore('scheduler', () => {
  const tasks        = ref([])
  const activeAlarms = ref([])
  const notifPerm    = ref(typeof Notification !== 'undefined' ? Notification.permission : 'denied')

  // Track which task IDs already fired this cycle to avoid double-fire
  const _fired = new Set()
  let _timer = null

  // ── Persistence ───────────────────────────────────────────────────
  function _load() {
    try { tasks.value = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]') }
    catch { tasks.value = [] }
  }
  function _save() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks.value))
  }

  // ── CRUD ──────────────────────────────────────────────────────────
  function addTask(data) {
    const t = {
      id:           uid(),
      title:        data.title.trim(),
      description:  (data.description || '').trim(),
      datetime:     data.datetime,          // ISO – next scheduled fire time
      time:         data.time,              // 'HH:MM' – kept for recurrence math
      recurrence:   data.recurrence  || 'none',
      notifyBefore: data.notifyBefore ?? 0, // minutes before datetime to fire
      soundEnabled: data.soundEnabled ?? true,
      soundType:    data.soundType    || 'default',
      enabled:      true,
      createdAt:    new Date().toISOString(),
    }
    tasks.value.push(t)
    _save()
    return t
  }

  function updateTask(id, changes) {
    const i = tasks.value.findIndex(t => t.id === id)
    if (i !== -1) { tasks.value[i] = { ...tasks.value[i], ...changes }; _save() }
  }

  function deleteTask(id) {
    tasks.value        = tasks.value.filter(t => t.id !== id)
    activeAlarms.value = activeAlarms.value.filter(a => a.id !== id)
    _fired.delete(id)
    _save()
  }

  function toggleTask(id) {
    const t = tasks.value.find(t => t.id === id)
    if (t) updateTask(id, { enabled: !t.enabled })
  }

  // ── Alarms ────────────────────────────────────────────────────────
  function dismissAlarm(id) {
    activeAlarms.value = activeAlarms.value.filter(a => a.id !== id)
    _fired.delete(id)
  }

  function snoozeAlarm(id, minutes) {
    const snoozedAt = new Date(Date.now() + minutes * 60_000)
    const hh = String(snoozedAt.getHours()).padStart(2, '0')
    const mm = String(snoozedAt.getMinutes()).padStart(2, '0')
    updateTask(id, {
      datetime:   snoozedAt.toISOString(),
      time:       `${hh}:${mm}`,
      enabled:    true,
    })
    dismissAlarm(id)
  }

  function _fireAlarm(task) {
    if (_fired.has(task.id)) return
    _fired.add(task.id)

    if (!activeAlarms.value.find(a => a.id === task.id)) {
      activeAlarms.value.push({ ...task })
    }

    // Browser push notification
    if (typeof Notification !== 'undefined' && Notification.permission === 'granted') {
      new Notification(`⏰ ${task.title}`, {
        body:              task.description || 'Lembrete agendado',
        icon:              '/favicon.ico',
        tag:               `ws-task-${task.id}`,
        requireInteraction: true,
      })
    }

    // Schedule next occurrence
    const next = calcNext(task, task.datetime)
    if (next) {
      updateTask(task.id, { datetime: next })
      _fired.delete(task.id) // allow recurrence to re-fire
    } else {
      updateTask(task.id, { enabled: false })
    }
  }

  function checkAlarms() {
    const now = Date.now()
    tasks.value.forEach(task => {
      if (!task.enabled) return
      const fireAt = new Date(task.datetime).getTime() - task.notifyBefore * 60_000
      const diff   = now - fireAt
      if (diff >= 0 && diff < FIRE_WIN_MS) _fireAlarm(task)
    })
  }

  // ── Notifications permission ──────────────────────────────────────
  async function requestPermission() {
    if (typeof Notification === 'undefined') return
    if (Notification.permission === 'default') {
      notifPerm.value = await Notification.requestPermission()
    } else {
      notifPerm.value = Notification.permission
    }
  }

  // ── Lifecycle ────────────────────────────────────────────────────
  function init() {
    _load()
    requestPermission()
    checkAlarms()
    _timer = setInterval(checkAlarms, CHECK_MS)
  }

  function destroy() {
    if (_timer) clearInterval(_timer)
  }

  // ── Computed ─────────────────────────────────────────────────────
  const sortedTasks = computed(() =>
    [...tasks.value].sort((a, b) => new Date(a.datetime) - new Date(b.datetime))
  )

  return {
    tasks, activeAlarms, notifPerm, sortedTasks,
    addTask, updateTask, deleteTask, toggleTask,
    dismissAlarm, snoozeAlarm,
    requestPermission, init, destroy,
  }
})
