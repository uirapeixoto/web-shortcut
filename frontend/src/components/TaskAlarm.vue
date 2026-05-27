<template>
  <Teleport to="body">
    <TransitionGroup name="alarm-pop" tag="div" class="alarm-stack">
      <div
        v-for="(alarm, idx) in scheduler.activeAlarms"
        :key="alarm.id"
        class="alarm-card"
        :style="{ '--stk': idx }"
        :class="{ 'alarm-card--back': idx > 0 }"
      >
        <!-- Only fully interactive for the top alarm -->
        <template v-if="idx === 0">
          <div class="alarm-pulse-ring"></div>

          <div class="alarm-icon">
            <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
              <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
              <line x1="12" y1="2" x2="12" y2="4"/>
            </svg>
          </div>

          <div class="alarm-sound-type">{{ SOUND_LABELS[alarm.soundType] || 'Padrão' }}</div>
          <h2 class="alarm-title">{{ alarm.title }}</h2>
          <p class="alarm-desc" v-if="alarm.description">{{ alarm.description }}</p>
          <div class="alarm-time">{{ fmtDatetime(alarm.datetime, alarm.notifyBefore) }}</div>

          <div class="alarm-snooze">
            <span class="snooze-label">Adiar:</span>
            <button class="snooze-btn" @click="snooze(alarm.id, 5)">5 min</button>
            <button class="snooze-btn" @click="snooze(alarm.id, 10)">10 min</button>
            <button class="snooze-btn" @click="snooze(alarm.id, 15)">15 min</button>
          </div>

          <button class="alarm-dismiss" @click="dismiss(alarm.id)">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            Dispensar
          </button>

          <div class="alarm-queue" v-if="scheduler.activeAlarms.length > 1">
            +{{ scheduler.activeAlarms.length - 1 }} alarme{{ scheduler.activeAlarms.length > 2 ? 's' : '' }} na fila
          </div>
        </template>

        <!-- Background card peek -->
        <template v-else>
          <div class="alarm-back-title">{{ alarm.title }}</div>
        </template>
      </div>
    </TransitionGroup>
  </Teleport>
</template>

<script setup>
import { watch, onUnmounted } from 'vue'
import { useSchedulerStore } from '../store/scheduler.js'
import { useAlarmSound } from '../composables/useAlarmSound.js'

const scheduler = useSchedulerStore()
const sound = useAlarmSound()

const SOUND_LABELS = { gentle: 'Alarme suave', default: 'Alarme padrão', urgent: 'Alarme urgente' }

watch(
  () => scheduler.activeAlarms.length,
  (len, prev) => {
    if (len > 0 && prev === 0) {
      // First alarm — start sound based on the topmost alarm's soundType
      const top = scheduler.activeAlarms[0]
      if (top?.soundEnabled !== false) sound.play(top?.soundType || 'default')
    }
    if (len === 0) sound.stop()
  }
)

onUnmounted(sound.stop)

function dismiss(id) {
  scheduler.dismissAlarm(id)
  if (scheduler.activeAlarms.length === 0) sound.stop()
}

function snooze(id, mins) {
  scheduler.snoozeAlarm(id, mins)
  if (scheduler.activeAlarms.length === 0) sound.stop()
}

function fmtDatetime(iso, notifyBefore = 0) {
  const d = new Date(new Date(iso).getTime() + notifyBefore * 60_000)
  return d.toLocaleString('pt-BR', { weekday: 'short', day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' })
}
</script>

<style scoped>
/* ── Stack container ────────────────────────────── */
.alarm-stack {
  position: fixed;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  pointer-events: none;
}

/* ── Card ───────────────────────────────────────── */
.alarm-card {
  position: absolute;
  pointer-events: all;
  background: #0f172a;
  border: 1px solid rgba(99,102,241,0.3);
  border-radius: 20px;
  padding: 36px 32px 28px;
  width: min(420px, 90vw);
  text-align: center;
  box-shadow: 0 30px 80px rgba(0,0,0,0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  transform: translateY(calc(var(--stk) * 12px)) scale(calc(1 - var(--stk) * 0.04));
  z-index: calc(100 - var(--stk));
  transition: transform 0.3s ease;
}
.alarm-card--back {
  background: #1e293b;
  border-color: rgba(99,102,241,0.15);
  pointer-events: none;
  padding: 16px 24px;
}

/* ── Pulse ring ─────────────────────────────────── */
.alarm-pulse-ring {
  position: absolute;
  inset: -12px;
  border-radius: 28px;
  border: 2px solid rgba(99,102,241,0.4);
  animation: pulse-ring 1.8s ease-out infinite;
  pointer-events: none;
}
@keyframes pulse-ring {
  0%   { opacity: 1; transform: scale(1); }
  100% { opacity: 0; transform: scale(1.06); }
}

/* ── Icon ───────────────────────────────────────── */
.alarm-icon {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: rgba(99,102,241,0.12);
  display: flex; align-items: center; justify-content: center;
  color: #818cf8;
  animation: bell-swing 0.6s ease-in-out infinite alternate;
  margin-bottom: 4px;
}
@keyframes bell-swing {
  from { transform: rotate(-10deg); }
  to   { transform: rotate(10deg);  }
}

.alarm-sound-type {
  font-size: 0.68rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #6366f1;
}

.alarm-title {
  font-size: 1.3rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
  line-height: 1.3;
}

.alarm-desc {
  font-size: 0.88rem;
  color: #94a3b8;
  margin: 0;
  max-width: 300px;
  line-height: 1.5;
}

.alarm-time {
  font-size: 0.78rem;
  color: #475569;
  font-variant-numeric: tabular-nums;
}

/* ── Snooze ─────────────────────────────────────── */
.alarm-snooze {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 8px;
  flex-wrap: wrap;
  justify-content: center;
}
.snooze-label {
  font-size: 0.75rem;
  color: #64748b;
}
.snooze-btn {
  padding: 5px 12px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.04);
  color: #94a3b8;
  font-size: 0.78rem;
  cursor: pointer;
  transition: background 0.15s, color 0.15s, border-color 0.15s;
}
.snooze-btn:hover {
  background: rgba(99,102,241,0.15);
  border-color: rgba(99,102,241,0.4);
  color: #a5b4fc;
}

/* ── Dismiss ─────────────────────────────────────── */
.alarm-dismiss {
  display: flex; align-items: center; gap: 6px;
  padding: 10px 28px;
  border-radius: 10px;
  border: none;
  background: #6366f1;
  color: #fff;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  margin-top: 4px;
  transition: background 0.15s;
}
.alarm-dismiss:hover { background: #4f46e5; }

/* ── Queue indicator ─────────────────────────────── */
.alarm-queue {
  font-size: 0.7rem;
  color: #475569;
  margin-top: 2px;
}

/* ── Background card peek text ───────────────────── */
.alarm-back-title {
  font-size: 0.85rem;
  color: #475569;
  font-weight: 500;
}

/* ── Transitions ─────────────────────────────────── */
.alarm-pop-enter-active { animation: alarm-in 0.35s cubic-bezier(0.34, 1.56, 0.64, 1); }
.alarm-pop-leave-active { animation: alarm-out 0.25s ease-in forwards; }
@keyframes alarm-in  { from { opacity: 0; transform: scale(0.7) translateY(40px); } to { opacity: 1; } }
@keyframes alarm-out { from { opacity: 1; } to { opacity: 0; transform: scale(0.85) translateY(-20px); } }
</style>
