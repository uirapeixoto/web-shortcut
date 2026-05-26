# Web Shortcut Manager

Painel pessoal para organizar e acessar links e atalhos web com rapidez. Interface dark moderna com categorias, editor Markdown e quadro Kanban integrados.

## Visão geral

```
web-shortcut/
├── backend/        # API REST — FastAPI + SQLAlchemy + SQLite
├── frontend/       # SPA — Vue 3 + Vite + Pinia
└── docker-compose.yml
```

A comunicação entre frontend e backend é feita via proxy Nginx — todas as chamadas para `/api/*` são encaminhadas internamente para o serviço `backend:8000`, sem expor a API diretamente.

## Funcionalidades

- **Atalhos** — cadastro, edição e remoção de links organizados por categorias com ícone e cor personalizados
- **Categorias** — criação e gestão de categorias com ícone emoji e cor de destaque
- **Admin** — painel para gerenciar categorias e atalhos via tabelas editáveis
- **Editor Markdown** — editor/leitor com suporte a diagramas Mermaid, split view, persistência no localStorage e atalho `Ctrl+M`
- **Kanban** — quadro estilo Trello com drag & drop, checklists, etiquetas e persistência no localStorage; atalho `Ctrl+K`

## Tecnologias

| Camada | Stack |
|---|---|
| Frontend | Vue 3 · Vite · Pinia · Vue Router |
| Backend | FastAPI · SQLAlchemy · Pydantic v2 |
| Banco de dados | SQLite (arquivo persistido em volume Docker) |
| Servidor | Nginx (proxy reverso + SPA) |
| Infra | Docker · Docker Compose |

## Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) e Docker Compose v2+
- **Ou**, para desenvolvimento local: Node.js 20+ e Python 3.12+

## Rodando com Docker (recomendado)

```bash
git clone <url-do-repositorio>
cd web-shortcut

docker compose up --build
```

A aplicação estará disponível em **http://localhost:3000**.

O banco de dados SQLite é armazenado em um volume Docker nomeado (`db-data`) e sobrevive a reinicializações do container.

Para parar:

```bash
docker compose down
```

Para apagar também os dados do banco:

```bash
docker compose down -v
```

## Desenvolvimento local

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8000
```

API disponível em `http://localhost:8000`.
Documentação interativa: `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Interface disponível em `http://localhost:5173`.

O Vite está configurado para fazer proxy de `/api` → `http://backend:8000` em desenvolvimento.

## API — endpoints principais

| Método | Rota | Descrição |
|---|---|---|
| `GET` | `/categories/` | Lista todas as categorias |
| `POST` | `/categories/` | Cria uma categoria |
| `PUT` | `/categories/{id}` | Atualiza uma categoria |
| `DELETE` | `/categories/{id}` | Remove uma categoria (e seus atalhos) |
| `GET` | `/shortcuts/` | Lista atalhos (aceita `?category_id=N`) |
| `POST` | `/shortcuts/` | Cria um atalho |
| `PUT` | `/shortcuts/{id}` | Atualiza um atalho |
| `DELETE` | `/shortcuts/{id}` | Remove um atalho |

## Estrutura do banco de dados

```
categories
  id, name, icon, color, order

shortcuts
  id, name, url, description, icon, color, order, category_id → categories.id
```

## Atalhos de teclado

| Atalho | Ação |
|---|---|
| `Ctrl+M` | Abre / fecha o Editor Markdown |
| `Ctrl+K` | Abre / fecha o Kanban |
| `Esc` | Fecha o painel ativo |
