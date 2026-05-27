# PR-005 — Agendador de Tarefas com Alarmes

**Branch:** `feat/task-scheduler`  
**Base:** `main`  
**Status:** Merged  
**Data:** 2026-05  

---

## Resumo

Agendador de compromissos com alarme sonoro (Web Audio API), notificações push nativas, tarefas recorrentes, soneca (snooze) e aviso antecipado. Persiste no `localStorage`. Abre com `Ctrl+A`. Funciona enquanto a aba do browser estiver aberta.

---

## Motivação

O painel já concentrava links, anotações e tarefas Kanban, mas sem lembretes temporais. Um agendador integrado permite criar alertas sem abrir um calendário externo — especialmente útil para compromissos recorrentes de rotina.

---

## Mudanças

### Novos arquivos

| Arquivo | Descrição |
|---|---|
| `src/store/scheduler.js` | Store Pinia: CRUD de tarefas, timer, lógica de disparo |
| `src/composables/useAlarmSound.js` | Geração de tons via Web Audio API |
| `src/components/TaskScheduler.vue` | Painel lateral: lista de tarefas + formulário |
| `src/components/TaskAlarm.vue` | Overlay de alarme ativo com snooze |

### Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/App.vue` | `scheduler.init()` no onMounted + `<TaskAlarm />` sempre montado |
| `src/components/SideMenu.vue` | Botão "Agendador" + `Ctrl+A` + ponto vermelho quando há alarme |

---

## Arquitetura

### Pipeline de disparo

```
App.vue:onMounted
  └─ scheduler.init()
       ├─ Carrega tarefas do localStorage
       ├─ Solicita permissão de notificações
       ├─ checkAlarms() imediatamente
       └─ setInterval(checkAlarms, 30_000)

checkAlarms()
  └─ Para cada task com enabled=true
       ├─ fireAt = datetime - notifyBefore minutos
       ├─ diff = now - fireAt
       ├─ Se diff ∈ [0, 90_000ms]  → _fireAlarm(task)
       └─ _fired Set evita duplo-disparo no mesmo ciclo

_fireAlarm(task)
  ├─ Adiciona task a activeAlarms[]
  ├─ Notification API se permissão granted
  └─ Recalcula e salva próxima ocorrência
       ├─ recurrence != none → updateTask({ datetime: next })
       └─ recurrence == none → updateTask({ enabled: false })
```

### Janela de segurança

O intervalo de 30 segundos pode sofrer atraso em abas em background (throttling do browser). A janela `FIRE_WIN_MS = 90_000` (90s) captura alarmes que deveriam ter disparado mas foram atrasados pelo scheduler do browser.

### Cálculo de recorrência

```javascript
calcNext(task, afterIso) {
  // weekdays: pula sábado (+2) e domingo (+1)
  // monthly:  setMonth(+1) — JS corrige overflow de dias automaticamente
  // Sempre define hora via setHours(h, m, 0, 0)
}
```

---

## Modelo de Dados (localStorage: `ws_scheduled_tasks`)

```json
[
  {
    "id":           "l8x2a9bcd",
    "title":        "Daily standup",
    "description":  "Reunião de equipe",
    "datetime":     "2026-05-27T09:00:00.000Z",
    "time":         "09:00",
    "recurrence":   "weekdays",
    "notifyBefore": 5,
    "soundEnabled": true,
    "soundType":    "default",
    "enabled":      true,
    "createdAt":    "2026-05-26T14:30:00.000Z"
  }
]
```

**Por que `time` separado?**  
O campo `datetime` é atualizado para a próxima ocorrência após cada disparo. O campo `time` preserva o horário original do dia para calcular corretamente as próximas ocorrências sem re-parsear o ISO.

---

## Sons (Web Audio API)

Sem arquivos externos — tones gerados programaticamente via `OscillatorNode` + `GainNode`:

| Padrão | Frequências | Ritmo | Volume | Repetição |
|---|---|---|---|---|
| `gentle` | 440 → 550 → 660 Hz (ascendente) | 0.45s entre notas | 25% | a cada 5s |
| `default` | 880 Hz × 5 | 0.35s entre beeps | 50% | a cada 3s |
| `urgent` | 880 / 1100 Hz alternado × 8 | 0.18s entre beeps | 70% | a cada 2s |

**Envelope de amplitude:**
```
gain.linearRampToValueAtTime(vol, t + 0.015)   // attack rápido
gain.exponentialRampToValueAtTime(0.001, t + 0.22) // decay natural
```

**Preview**: selecionar um tipo no formulário toca 3 segundos de preview.

---

## Notificações Push

Usa a **Web Notifications API** (não Web Push):
- Requer permissão explícita do usuário (solicitada na primeira criação de tarefa)
- Funciona com a aba em background, mas **não** com o browser fechado
- `requireInteraction: true` — notificação permanece até o usuário dispensar
- Tag única por tarefa evita notificações duplicadas na mesma sessão

---

## Funcionalidades do Formulário

| Campo | Tipo | Validação |
|---|---|---|
| Título | Texto | Obrigatório, max 80 chars |
| Descrição | Textarea | Opcional, max 300 chars |
| Data | Date picker | Obrigatório |
| Hora | Time picker | Obrigatório |
| Repetição | Select | none / daily / weekdays / weekly / monthly |
| Avisar antes | Select | 0 / 5 / 10 / 15 / 30 min |
| Som | Toggle | — |
| Tipo de alarme | 3 botões | gentle / default / urgent |

---

## Overlay de Alarme (TaskAlarm.vue)

- Teleport para `body`, sempre montado, gerenciado pelo store
- Mostra um card por vez (o mais antigo é tratado primeiro)
- Cards adicionais aparecem "empilhados" atrás com offset visual
- Animação de sino pulsante durante o alarme
- **Dismiss**: remove o alarme da fila e para o som (se fila vazia)
- **Snooze** (5/10/15 min): cria uma nova ocorrência no horário futuro e remove da fila

---

## Ponto na Sidebar

O `SideMenu.vue` exibe um ponto vermelho pulsante sobre o botão do agendador enquanto `scheduler.activeAlarms.length > 0`. Serve como indicador visual mesmo com o painel fechado.

---

## Como Testar

### Tarefa única
1. `Ctrl+A` → "Nova tarefa"
2. Defina título, data/hora para daqui ~1 minuto, repetição "Não repetir"
3. Salve e aguarde
4. Ao disparar: overlay aparece + som + notificação do browser

### Tarefa recorrente
1. Crie com repetição "Diariamente"
2. Após disparo, confirme que `datetime` foi atualizado para amanhã

### Snooze
1. Quando o alarme aparecer, clique "10 min"
2. Confirme que o alarme desaparece e o `datetime` foi atualizado

### Aviso antecipado
1. Crie tarefa com "15 minutos antes"
2. O disparo ocorre 15min antes do horário definido

### Múltiplos alarmes
1. Crie 3 tarefas para disparar no mesmo minuto
2. Confirme o stack visual e que cada um pode ser dispensado independentemente

---

## Limitações

| Limitação | Observação |
|---|---|
| Requer aba aberta | Service Worker com Push API exigiria backend VAPID |
| Sem iCloud/Google Calendar sync | Escopo futuro |
| Soneca cria nova ocorrência isolada | Após soneca, recorrência original continua no horário original |
| Timezone | Usa timezone local do browser; sem suporte a timezone customizado |
