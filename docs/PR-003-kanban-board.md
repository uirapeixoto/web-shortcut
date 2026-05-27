# PR-003 — Quadro Kanban

**Branch:** `feat/kanban-board`  
**Base:** `main`  
**Status:** Merged  
**Data:** 2026-05  

---

## Resumo

Quadro Kanban estilo Trello com colunas configuráveis, cards com checklist, etiquetas coloridas e data de vencimento. Drag & drop nativo HTML5. Persiste no `localStorage`. Abre com `Ctrl+K`.

---

## Motivação

O painel já concentrava links e anotações, mas faltava um espaço para rastrear tarefas em andamento. Um Kanban integrado evita a necessidade de uma ferramenta externa para gestão de tarefas simples do dia a dia.

---

## Mudanças

### Novos arquivos

| Arquivo | Descrição |
|---|---|
| `src/components/KanbanBoard.vue` | Componente completo do Kanban |

### Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/components/SideMenu.vue` | Botão de abertura + atalho `Ctrl+K` |

---

## Funcionalidades Implementadas

### Colunas
- Adicionar / remover colunas
- Renomear por duplo clique
- Cor de acento personalizável (color picker)
- Contador de cards por coluna

### Cards
- Título (obrigatório) e descrição
- **Checklist**: adicionar itens, marcar como concluído, remover
- **Etiquetas**: cores predefinidas + texto personalizado
- **Data de vencimento**: exibida com alerta visual quando vencida
- Edição inline / modal de detalhe
- Remover card

### Drag & Drop
- API nativa HTML5 (`draggable`, `dragover`, `drop`)
- Arraste entre colunas com indicador visual de drop zone
- Reordenação dentro da mesma coluna

### Persistência
- Serialização JSON completa em `localStorage` a cada mudança
- Estrutura: `{ columns: [], cards: { [columnId]: Card[] } }`

### Tela cheia
- Toggle para maximizar o painel

---

## Modelo de Dados (localStorage)

```json
{
  "boardTitle": "Meu Kanban",
  "columns": [
    { "id": "col_abc", "title": "A fazer", "color": "#6366f1", "editingTitle": false }
  ],
  "cards": {
    "col_abc": [
      {
        "id": "card_xyz",
        "title": "Tarefa de exemplo",
        "description": "",
        "labels": [{ "color": "#ef4444", "text": "Urgente" }],
        "checklist": [{ "text": "Subtarefa", "done": false }],
        "dueDate": "2026-06-01"
      }
    ]
  }
}
```

---

## Decisões de Design

**Drag & Drop nativo vs biblioteca**: A API HTML5 nativa é suficiente para o caso de uso e evita ~50kb de dependência extra. A principal limitação (sem animação de reordenação suave) foi aceita.

**`cards` como objeto keyed por `columnId`**: Permite mover cards entre colunas como uma operação de splice + push sem reindexar todos os cards — O(1) de acesso.

**Estado de edição no objeto da coluna** (`editingTitle: false`): Simplifica o template ao eliminar um Map ou ref separado para controlar qual coluna está em edição.

**Color picker de coluna por popover inline**: Evita modal externo. O picker fecha ao clicar fora via `@click.outside` handler.

---

## Como Testar

1. Pressione `Ctrl+K` para abrir o Kanban
2. Crie uma coluna (botão "+ Coluna")
3. Adicione um card — preencha título, etiqueta e data de vencimento
4. Adicione itens ao checklist e marque alguns como concluídos
5. Arraste o card para outra coluna
6. Feche e reabra — confirme persistência
7. Renomeie uma coluna por duplo clique no título
8. Mude a cor de acento de uma coluna
9. Teste tela cheia

---

## Limitações

- Não sincroniza com o backend — dados ficam no browser
- Sem histórico/undo de ações
- Sem colaboração em tempo real
