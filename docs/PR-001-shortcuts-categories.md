# PR-001 — Atalhos e Categorias

**Branch:** `feat/shortcuts-categories`  
**Base:** `main`  
**Status:** Merged  
**Data:** 2026-05  

---

## Resumo

Implementação do núcleo da aplicação: modelo de dados, API REST e interface para gerenciar categorias e atalhos web. Inclui layout principal com sidebar de navegação, grid de atalhos e a landing page.

---

## Motivação

O objetivo central do projeto é ter um painel único para acessar links com rapidez. Links sem organização perdem utilidade — categorias com ícone e cor permitem localização visual instantânea. A sidebar colapsável maximiza espaço em telas menores.

---

## Mudanças

### Backend — novos arquivos

| Arquivo | Descrição |
|---|---|
| `backend/app.py` | Ponto de entrada FastAPI com CORS e inclusão de routers |
| `backend/database.py` | Modelos `Category` e `Shortcut` + `init_db()` |
| `backend/routes/categories.py` | CRUD completo de categorias |
| `backend/routes/shortcuts.py` | CRUD completo de atalhos com filtro por `category_id` |
| `backend/requirements.txt` | `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic` |

### Frontend — novos arquivos

| Arquivo | Descrição |
|---|---|
| `src/main.js` | Bootstrap da app Vue 3 com Pinia e Router |
| `src/App.vue` | Layout raiz: TopMenu + SideMenu + router-view |
| `src/store/index.js` | Store Pinia com fetch/save de categorias e atalhos |
| `src/router/index.js` | Rotas `/`, `/shortcuts`, `/shortcuts/:categoryId` |
| `src/views/Landing.vue` | Página inicial com CTA |
| `src/views/Shortcuts.vue` | Grid de atalhos com filtro por categoria |
| `src/components/TopMenu.vue` | Barra superior com toggle da sidebar |
| `src/components/SideMenu.vue` | Navegação lateral com lista de categorias |
| `src/components/ShortcutCard.vue` | Card de atalho com ícone, cor e link |
| `src/style.css` | Design system: variáveis CSS, dark mode |

---

## Modelo de Dados

```
categories (id, name, icon, color, order)
    │
    └── shortcuts (id, name, url, description, icon, color, order, category_id)
                  CASCADE DELETE ao remover categoria
```

---

## Decisões de Design

**Proxy Nginx para `/api/`**: evita CORS e permite que frontend e backend sejam servidos na mesma origem. Em dev, o Vite proxy replica esse comportamento.

**`order` como campo inteiro**: permite ordenação customizada sem drag & drop — incrementado manualmente via admin. Futuro: substituir por drag & drop.

**CASCADE DELETE em shortcuts**: remover uma categoria remove automaticamente todos seus atalhos, mantendo integridade referencial sem lógica adicional no backend.

**Sidebar colapsável**: `store.sideOpen` persiste na sessão. Em mobile (`< 768px`), fecha automaticamente ao navegar.

---

## Como Testar

1. `docker compose up --build`
2. Acesse `http://localhost:3000/admin`
3. Crie uma categoria (ex: "Desenvolvimento", ícone 💻, cor azul)
4. Crie um atalho vinculado a essa categoria
5. Acesse `/shortcuts` e confirme que o card aparece
6. Filtre pela categoria na sidebar
7. Teste colapsar/expandir a sidebar

---

## API testável via Swagger

```
http://localhost:8000/docs
```
