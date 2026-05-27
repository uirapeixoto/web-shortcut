# PR-002 — Editor Markdown com Mermaid

**Branch:** `feat/markdown-editor`  
**Base:** `main`  
**Status:** Merged  
**Data:** 2026-05  

---

## Resumo

Editor Markdown flutuante com preview em tempo real, suporte a diagramas Mermaid, exportação de arquivo e persistência automática no `localStorage`. Abre como painel overlay com atalho `Ctrl+M`.

---

## Motivação

Durante o uso diário do painel, surgiu a necessidade de escrever anotações, rascunhos e documentações rápidas sem sair da aplicação. Integrar o editor ao painel evita alternar entre apps — o texto persiste na sessão e pode ser exportado como arquivo `.md`.

---

## Mudanças

### Novos arquivos

| Arquivo | Descrição |
|---|---|
| `src/components/MarkdownEditor.vue` | Componente completo do editor |

### Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/components/SideMenu.vue` | Botão de abertura + atalho `Ctrl+M` |
| `package.json` | Adicionado `marked`, `mermaid` |

---

## Funcionalidades Implementadas

### Modos de visualização
- **Edição** — textarea puro, sem preview
- **Split** — editor lado a lado com preview
- **Preview** — apenas a renderização HTML

### Mermaid
Diagramas delimitados por ` ```mermaid ``` ` são detectados automaticamente após cada render e inicializados via `mermaid.init()`. Suporte a: flowchart, sequence, gantt, class diagram, etc.

### Persistência
Conteúdo salvo automaticamente em `localStorage` a cada digitação (debounce implícito via reatividade Vue). Restaurado ao reabrir.

### Exportação
Botão "Baixar .md" gera um `Blob` e dispara download com o nome `documento.md`.

### Tela cheia
Botão toggle maximiza o painel para a tela completa.

---

## Decisões de Design

**`marked` vs renderização manual**: `marked` é leve (~45kb), bem mantido e converte Markdown → HTML de forma segura sem necessidade de sanitização adicional para uso pessoal.

**`mermaid.init()` após render**: Mermaid precisa re-inicializar os blocos a cada mudança de conteúdo porque o HTML é substituído inteiro. `setTimeout(0)` após atualizar o DOM garante que os elementos existem antes da inicialização.

**`Teleport to="body"`**: Evita conflito de z-index com a sidebar e garante que o overlay cobre a tela inteira independentemente de onde o componente está na árvore.

**Ctrl+M em `window`**: O listener é global (não apenas no componente) para funcionar em qualquer página sem focar o editor primeiro.

---

## Como Testar

1. Abra a aplicação e pressione `Ctrl+M`
2. Digite texto Markdown no editor
3. Alterne para modo Split — preview aparece à direita
4. Adicione um diagrama:
   ```
   ```mermaid
   graph TD
     A[Início] --> B{Decisão}
     B -->|Sim| C[Fim]
     B -->|Não| A
   ```
   ```
5. Feche e reabra o editor — conteúdo deve ser restaurado
6. Clique em "Baixar .md" e confirme o download

---

## Dependências Adicionadas

| Pacote | Versão | Uso |
|---|---|---|
| `marked` | ^18.0 | Parse Markdown → HTML |
| `mermaid` | ^11.15 | Renderização de diagramas |
