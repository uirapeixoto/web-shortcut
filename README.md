# Web Shortcut Manager

Painel pessoal de produtividade — organize links, leia EPUBs, escreva em Markdown, gerencie tarefas no Kanban e receba alertas de compromissos, tudo em um único lugar.

```
web-shortcut/
├── backend/          # API REST — FastAPI + SQLAlchemy + SQLite
├── frontend/         # SPA — Vue 3 + Vite + Pinia
├── docs/             # Documentação técnica (SDD + PRs)
└── docker-compose.yml
```

---

## Funcionalidades

| Módulo | Descrição | Atalho |
|---|---|---|
| **Atalhos** | Cadastro de links com categoria, ícone e cor | — |
| **Admin** | Painel CRUD para categorias e atalhos | — |
| **Editor Markdown** | Editor/leitor com Mermaid, split view e localStorage | `Ctrl+M` |
| **Kanban** | Quadro drag & drop com checklists e etiquetas | `Ctrl+K` |
| **Biblioteca EPUB** | Upload e leitura de livros `.epub` com slide horizontal | — |
| **Agendador** | Tarefas com alarme sonoro, notificações push e soneca | `Ctrl+A` |

---

## Stack

| Camada | Tecnologia |
|---|---|
| Frontend | Vue 3 · Vite · Pinia · Vue Router · epubjs |
| Backend | FastAPI · SQLAlchemy · Pydantic v2 · Python 3.12 |
| Banco | SQLite (volume Docker persistido) |
| Infra | Nginx (proxy + SPA) · Docker Compose |

---

## Rodando com Docker

```bash
git clone <url>
cd web-shortcut
docker compose up --build
```

Disponível em **http://localhost:3000**.

```bash
docker compose down        # para
docker compose down -v     # para + apaga dados
```

## Desenvolvimento local

**Backend**
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8001
```
Swagger: `http://localhost:8001/docs`

**Frontend**
```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

---

## API — referência rápida

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/categories/` | Lista categorias |
| `POST` | `/categories/` | Cria categoria |
| `PUT` | `/categories/{id}` | Atualiza categoria |
| `DELETE` | `/categories/{id}` | Remove categoria e atalhos |
| `GET` | `/shortcuts/` | Lista atalhos (`?category_id=N`) |
| `POST` | `/shortcuts/` | Cria atalho |
| `PUT` | `/shortcuts/{id}` | Atualiza atalho |
| `DELETE` | `/shortcuts/{id}` | Remove atalho |
| `GET` | `/ebooks/` | Lista livros |
| `POST` | `/ebooks/upload` | Upload de `.epub` |
| `GET` | `/ebooks/{id}/book.epub` | Serve o arquivo epub |
| `DELETE` | `/ebooks/{id}` | Remove livro e arquivo |

---

## Documentação técnica

| Documento | Descrição |
|---|---|
| [`docs/SDD.md`](docs/SDD.md) | Software Design Document — arquitetura, modelos, decisões |
| [`docs/PR-001-shortcuts-categories.md`](docs/PR-001-shortcuts-categories.md) | PR: Atalhos e categorias |
| [`docs/PR-002-markdown-editor.md`](docs/PR-002-markdown-editor.md) | PR: Editor Markdown + Mermaid |
| [`docs/PR-003-kanban-board.md`](docs/PR-003-kanban-board.md) | PR: Quadro Kanban |
| [`docs/PR-004-epub-reader.md`](docs/PR-004-epub-reader.md) | PR: Biblioteca e leitor EPUB |
| [`docs/PR-005-task-scheduler.md`](docs/PR-005-task-scheduler.md) | PR: Agendador com alarmes |
| [`docs/PR-006-admin-panel.md`](docs/PR-006-admin-panel.md) | PR: Painel administrativo |

---

## Estrutura de arquivos

```
backend/
├── app.py               # Ponto de entrada FastAPI
├── database.py          # Modelos SQLAlchemy + init_db
├── requirements.txt
├── routes/
│   ├── categories.py    # CRUD categorias
│   ├── shortcuts.py     # CRUD atalhos
│   └── ebooks.py        # Upload/serve EPUBs
├── data/                # shortcuts.db (gerado em runtime)
└── upload/ebook/epub/   # EPUBs enviados (gerado em runtime)

frontend/src/
├── App.vue              # Root: layout + inicialização do scheduler
├── main.js
├── style.css
├── router/index.js
├── store/
│   ├── index.js         # Categorias e atalhos (API)
│   └── scheduler.js     # Agendador (localStorage)
├── composables/
│   └── useAlarmSound.js # Geração de alarme via Web Audio API
├── components/
│   ├── TopMenu.vue
│   ├── SideMenu.vue
│   ├── ShortcutCard.vue
│   ├── MarkdownEditor.vue
│   ├── KanbanBoard.vue
│   ├── EpubFlipReader.vue
│   ├── TaskScheduler.vue
│   └── TaskAlarm.vue
└── views/
    ├── Landing.vue
    ├── Shortcuts.vue
    ├── Admin.vue
    └── Ebooks.vue
```

## Atalhos de teclado

| Atalho | Ação |
|---|---|
| `Ctrl+M` | Abre / fecha o Editor Markdown |
| `Ctrl+K` | Abre / fecha o Kanban |
| `Ctrl+A` | Abre / fecha o Agendador |
| `Esc` | Fecha o painel ativo / cancela carregamento |
| `← →` | Navega páginas no leitor EPUB |
