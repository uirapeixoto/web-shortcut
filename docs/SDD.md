# Software Design Document — Web Shortcut Manager

**Versão:** 1.0  
**Data:** 2026-05-26  
**Autor:** Uira Peixoto  

---

## 1. Visão Geral

O Web Shortcut Manager é um painel pessoal de produtividade self-hosted que centraliza:

- Acesso rápido a links organizados por categoria
- Editor Markdown com suporte a diagramas Mermaid
- Quadro Kanban para gestão de tarefas
- Biblioteca e leitor de livros EPUB
- Agendador de compromissos com alarme sonoro e notificações push

O sistema é composto por uma SPA Vue 3 servida via Nginx e uma API REST FastAPI, comunicando-se internamente via proxy reverso. Funcionalidades que não exigem persistência remota (Kanban, Markdown, Agendador) usam `localStorage` exclusivamente.

---

## 2. Arquitetura do Sistema

### 2.1 Diagrama de Implantação

```
┌─────────────────────────────────────────────────────────┐
│  Docker Compose                                         │
│                                                         │
│  ┌──────────────────────────────┐                       │
│  │  frontend (Nginx :80)        │  ◄── porta 3000 host  │
│  │                              │                       │
│  │  /          → SPA (Vue 3)    │                       │
│  │  /api/*     → proxy_pass     │──────────────────┐    │
│  └──────────────────────────────┘                  │    │
│                                                    ▼    │
│  ┌──────────────────────────────┐                       │
│  │  backend (uvicorn :8000)     │  ◄── interno only     │
│  │                              │                       │
│  │  FastAPI + SQLAlchemy        │                       │
│  │  SQLite  ← volume db-data    │                       │
│  │  EPUBs   ← volume epub-data  │                       │
│  └──────────────────────────────┘                       │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Fluxo de Dados

```
Browser
  │
  ├─ GET /          →  Nginx serve index.html (SPA)
  │
  ├─ GET /api/...   →  Nginx proxy → FastAPI → SQLite
  │                                              │
  └─ GET /api/ebooks/{id}/book.epub              │
                    →  Nginx proxy → FastAPI → Disco (EPUB)
```

### 2.3 Camadas da Aplicação

```
┌────────────────────────────────────────────────┐
│  Apresentação (Vue 3 Components / Views)       │
├────────────────────────────────────────────────┤
│  Estado (Pinia Stores + composables)           │
├────────────────────────────────────────────────┤
│  Roteamento (Vue Router)                       │
├────────────────────────────────────────────────┤
│  API HTTP (fetch nativo + Nginx proxy)         │
├────────────────────────────────────────────────┤
│  FastAPI Routes → Services → SQLAlchemy ORM   │
├────────────────────────────────────────────────┤
│  SQLite (persistência remota)                  │
│  localStorage (persistência local)             │
└────────────────────────────────────────────────┘
```

---

## 3. Banco de Dados

### 3.1 Modelo Relacional

```
categories
──────────────────────────
id          INTEGER  PK
name        TEXT     NOT NULL
icon        TEXT     DEFAULT '🔗'
color       TEXT     DEFAULT '#6366f1'
order       INTEGER  DEFAULT 0

shortcuts
──────────────────────────
id          INTEGER  PK
name        TEXT     NOT NULL
url         TEXT     NOT NULL
description TEXT     DEFAULT ''
icon        TEXT     DEFAULT '🌐'
color       TEXT     DEFAULT '#6366f1'
order       INTEGER  DEFAULT 0
category_id INTEGER  FK → categories.id  (CASCADE DELETE)

ebooks
──────────────────────────
id            INTEGER  PK
title         TEXT     NOT NULL
filename      TEXT     NOT NULL        (UUID.epub no disco)
original_name TEXT     NOT NULL
size          INTEGER  DEFAULT 0       (bytes)
created_at    TEXT     DEFAULT ''      (ISO 8601)
```

### 3.2 Persistência Local (localStorage)

Duas chaves independentes no browser:

| Chave | Conteúdo | Gerenciada por |
|---|---|---|
| `ws_kanban` | JSON do quadro Kanban (colunas + cards) | `KanbanBoard.vue` |
| `ws_markdown` | Texto do editor Markdown | `MarkdownEditor.vue` |
| `ws_scheduled_tasks` | Array de tarefas agendadas | `store/scheduler.js` |

---

## 4. API REST

### 4.1 Endpoints

#### Categorias — `/categories`

| Método | Rota | Corpo | Resposta |
|---|---|---|---|
| `GET` | `/` | — | `CategoryOut[]` |
| `POST` | `/` | `CategoryIn` | `CategoryOut` |
| `PUT` | `/{id}` | `CategoryIn` | `CategoryOut` |
| `DELETE` | `/{id}` | — | `{ok: true}` |

```python
# CategoryIn / CategoryOut
{
  "name":  str,
  "icon":  str = "🔗",
  "color": str = "#6366f1",
  "order": int = 0,
  # CategoryOut adiciona:
  "id":    int
}
```

#### Atalhos — `/shortcuts`

| Método | Rota | Corpo | Resposta |
|---|---|---|---|
| `GET` | `/` | query `?category_id=N` | `ShortcutOut[]` |
| `POST` | `/` | `ShortcutIn` | `ShortcutOut` |
| `PUT` | `/{id}` | `ShortcutIn` | `ShortcutOut` |
| `DELETE` | `/{id}` | — | `{ok: true}` |

```python
# ShortcutIn
{
  "name":        str,
  "url":         str,
  "description": str = "",
  "icon":        str = "🌐",
  "color":       str = "#6366f1",
  "order":       int = 0,
  "category_id": int
}
```

#### Ebooks — `/ebooks`

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/` | Lista metadados de todos os livros |
| `POST` | `/upload` | Upload multipart de `.epub` |
| `GET` | `/{id}/book.epub` | Serve o arquivo EPUB |
| `DELETE` | `/{id}` | Remove registro + arquivo do disco |

### 4.2 Tratamento de Erros

Todos os endpoints retornam HTTP 404 com `{"detail": "..."}` quando o recurso não existe. Upload valida a extensão `.epub` e retorna 400 em caso inválido.

---

## 5. Frontend

### 5.1 Estrutura de Componentes

```
App.vue
├── TopMenu.vue          # Barra superior + toggle sidebar
├── SideMenu.vue         # Navegação lateral + atalhos de teclado
│   ├── MarkdownEditor.vue   (Teleport → body)
│   ├── KanbanBoard.vue      (Teleport → body)
│   └── TaskScheduler.vue    (Teleport → body)
├── router-view
│   ├── Landing.vue      # Página inicial pública
│   ├── Shortcuts.vue    # Grid de atalhos filtrado por categoria
│   ├── Admin.vue        # Tabelas CRUD de admin
│   └── Ebooks.vue       # Biblioteca + leitor EPUB
│       └── EpubFlipReader.vue  (Teleport → body)
└── TaskAlarm.vue        (Teleport → body, sempre montado)
```

### 5.2 Stores Pinia

#### `store/index.js` — Store Principal
- Estado: `categories[]`, `shortcuts[]`, `sideOpen`
- Ações: `fetchCategories()`, `fetchShortcuts()`, `saveCategory()`, `deleteCategory()`, `saveShortcut()`, `deleteShortcut()`
- Persistência: nenhuma (servidor como fonte da verdade)

#### `store/scheduler.js` — Agendador
- Estado: `tasks[]`, `activeAlarms[]`, `notifPerm`
- Computed: `sortedTasks` (ordenado por data)
- Ações: `addTask()`, `updateTask()`, `deleteTask()`, `toggleTask()`, `dismissAlarm()`, `snoozeAlarm()`, `checkAlarms()`, `init()`, `destroy()`
- Persistência: `localStorage` (`ws_scheduled_tasks`)
- Timer: `setInterval(checkAlarms, 30_000)` iniciado em `App.vue:onMounted`

### 5.3 Roteamento

| Rota | Componente | Descrição |
|---|---|---|
| `/` | `Landing.vue` | Página inicial (sem sidebar) |
| `/shortcuts` | `Shortcuts.vue` | Todos os atalhos |
| `/shortcuts/:categoryId` | `Shortcuts.vue` | Atalhos filtrados |
| `/admin` | `Admin.vue` | Painel administrativo |
| `/ebooks` | `Ebooks.vue` | Biblioteca EPUB |

### 5.4 Comunicação com a API

Todo `fetch` aponta para `/api/...`. Em produção (Docker), Nginx faz proxy para `http://backend:8000/`. Em desenvolvimento, `vite.config.js` configura proxy para `http://localhost:8001/`.

---

## 6. Módulos Principais

### 6.1 Leitor EPUB (`EpubFlipReader.vue`)

**Biblioteca:** epubjs 0.3.93

**Fluxo de inicialização:**
1. Recebe `props.url` terminando em `.epub` (ativa archive mode no epubjs)
2. `ePub(url)` → epubjs detecta extensão → baixa como binário → carrega via JSZip
3. `book.renderTo(el, { flow: 'paginated' })` → cria iframe sandboxed
4. `rendition.display()` com timeout de 20s → exibe primeira página
5. `book.locations.generate(1024)` em background → habilita barra de progresso

**Animação de slide:**
- Fase 1: `translateX(-100%)` (saída)
- Fase 2: posiciona nova página oposta (`translateX(100%)`) sem transição
- Fase 3: `translateX(0)` (entrada)

**Tratamento de erros:**
- Timeout de 20s → exibe mensagem de erro com botão "Tentar novamente"
- ESC ou botão fechar cancela o carregamento a qualquer momento
- `try/catch` em navegação e em `percentageFromCfi` para robustez

### 6.2 Agendador (`scheduler.js` + `TaskScheduler.vue` + `TaskAlarm.vue`)

**Modelo de dados (localStorage):**
```json
{
  "id":           "string (uid)",
  "title":        "string",
  "description":  "string",
  "datetime":     "ISO 8601 (próximo disparo)",
  "time":         "HH:MM (para recalcular recorrência)",
  "recurrence":   "none | daily | weekdays | weekly | monthly",
  "notifyBefore": 0,
  "soundEnabled": true,
  "soundType":    "gentle | default | urgent",
  "enabled":      true,
  "createdAt":    "ISO 8601"
}
```

**Cálculo de recorrência:**
- Após disparo, `calcNext(task, firedAt)` adiciona o intervalo à data do disparo e retorna o próximo ISO
- `weekdays` avança dias pulando sábado (→ +2) e domingo (→ +1)
- Tarefas `none` ficam `enabled: false` após o disparo

**Pipeline de disparo:**
```
setInterval (30s)
  └─ checkAlarms()
       ├─ Para cada task enabled
       ├─ fireAt = datetime - notifyBefore min
       ├─ Se (now - fireAt) em [0, 90s]
       │    ├─ Push para activeAlarms[]
       │    ├─ Notification API (se permissão granted)
       │    └─ Calcula e salva próxima ocorrência
       └─ _fired Set evita disparo duplo no mesmo ciclo
```

**Som (Web Audio API):**
- Sem arquivos externos — tones gerados via `OscillatorNode` + `GainNode`
- 3 padrões: `gentle` (440Hz, 3 notas, 5s), `default` (880Hz, 5 beeps, 3s), `urgent` (880/1100Hz alternado, 2s)
- Preview ao selecionar tipo no formulário (3 segundos)

### 6.3 Markdown Editor (`MarkdownEditor.vue`)

- Parse: `marked` (biblioteca)
- Diagramas: `mermaid` (inicializado após cada render)
- Modos: edição, split, preview
- Persistência: `localStorage` (chave `ws_markdown`)
- Exportação: download `.md`

### 6.4 Kanban Board (`KanbanBoard.vue`)

- Drag & drop nativo HTML5 (`draggable`, `dragover`, `drop`)
- Cards com: título, descrição, checklist, etiquetas coloridas, data de vencimento
- Colunas configuráveis com cor de acento
- Persistência: `localStorage` (chave `ws_kanban`)
- Tela cheia disponível

---

## 7. Segurança

| Aspecto | Decisão |
|---|---|
| EPUB iframe | `sandbox` sem `allow-scripts` — scripts do epub bloqueados intencionalmente |
| CORS | `allow_origins=["*"]` aceitável para uso self-hosted; restringir em produção compartilhada |
| Upload | Validação de extensão `.epub` no backend; nome de arquivo substituído por UUID |
| Notificações push | Usa Web Notifications API (requer interação do usuário para permissão) — sem backend VAPID |
| Autenticação | Não implementada — adequado para uso pessoal/self-hosted |
| SQLite | Banco local, não exposto; adequado para instância single-user |

---

## 8. Decisões de Design

### Por que localStorage para Kanban, Markdown e Agendador?
Essas funcionalidades são inteiramente pessoais e não precisam de sincronização entre dispositivos no escopo atual. Eliminar a dependência da API reduz latência e simplifica o backend.

### Por que epubjs em modo arquivo (archive)?
Epubjs detecta o modo pelo sufixo da URL. Servindo o arquivo como `/{id}/book.epub`, a biblioteca baixa o zip uma única vez e extrai todos os recursos internamente, evitando dezenas de requisições HTTP para cada capítulo/imagem.

### Por que Web Audio API para alarmes?
Elimina a necessidade de arquivos de áudio externos, funciona sem configuração de servidor e permite gerar padrões programáticos com controle preciso de frequência, volume e timing — incluindo preview interativo.

### Por que não Service Worker para o agendador?
Service Workers para push notifications requerem backend próprio com chaves VAPID e uma infraestrutura de subscrição. Para o escopo self-hosted atual, `setInterval` + Web Notifications API (com a aba aberta) é suficiente e muito mais simples de manter.

---

## 9. Limitações Conhecidas e Trabalho Futuro

| Item | Status |
|---|---|
| Autenticação / multi-usuário | Não implementado |
| Sincronização do Kanban/Markdown na API | Apenas localStorage |
| Agendador funciona só com aba aberta | Service Worker futuro |
| EPUB com scripts interativos | Bloqueados pelo sandbox |
| Mobile responsivo | Parcial (sidebar colapsável) |
| Testes automatizados | Não implementados |
| Ordenação drag & drop de atalhos | Não implementada |
