# PR-006 — Painel Administrativo

**Branch:** `feat/admin-panel`  
**Base:** `main`  
**Status:** Merged  
**Data:** 2026-05  

---

## Resumo

Painel de administração com tabelas inline-editáveis para gerenciar categorias e atalhos. Permite criar, editar campos diretamente na linha, reordenar e excluir sem sair da tela. Acessível via `/admin`.

---

## Motivação

O fluxo de criação de atalhos via modal separado era lento para cadastros em lote. O painel admin com edição inline reduz cliques: o usuário edita o campo diretamente na tabela, pressiona Enter e a mudança é salva — sem abrir modais.

---

## Mudanças

### Novos arquivos

| Arquivo | Descrição |
|---|---|
| `src/views/Admin.vue` | Painel com duas seções: Categorias e Atalhos |

### Arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/router/index.js` | Rota `/admin` |
| `src/store/index.js` | `saveCategory()`, `deleteCategory()`, `saveShortcut()`, `deleteShortcut()` |

---

## Funcionalidades

### Seção Categorias

| Operação | Comportamento |
|---|---|
| **Criar** | Linha em branco adicionada ao topo da tabela |
| **Editar** | Clique em qualquer célula → input inline ativo |
| **Ícone** | Picker de emoji ou texto livre |
| **Cor** | `<input type="color">` nativo |
| **Salvar** | Enter ou blur do campo → `PUT /categories/{id}` |
| **Excluir** | Botão lixeira → confirma + `DELETE /categories/{id}` |

### Seção Atalhos

| Operação | Comportamento |
|---|---|
| **Criar** | Linha em branco adicionada ao topo |
| **Editar** | Clique na célula → input inline |
| **Categoria** | Select com lista das categorias existentes |
| **URL** | Validação básica de formato |
| **Salvar** | Enter ou blur → `PUT /shortcuts/{id}` |
| **Excluir** | Botão lixeira + confirmação |

### Ordenação

Campo `order` (inteiro) exibido e editável nas tabelas. Permite controlar a posição sem drag & drop — basta digitar o número desejado.

---

## Decisões de Design

**Edição inline vs modais**: Modais interrompem o fluxo visual quando o usuário gerencia muitos itens em sequência. Edição inline mantém o contexto da lista completa visível enquanto edita.

**Confirmar ao remover categoria**: `DELETE /categories/{id}` aciona `CASCADE DELETE` nos atalhos vinculados — confirmação explícita evita perda acidental.

**Fetch no store, não na view**: `saveCategory()` e afins vivem no store para que o estado (lista de categorias) seja atualizado globalmente — a sidebar reflete a mudança sem reload.

**`/admin` sem guard de autenticação**: Aplicação self-hosted de uso pessoal. Adicionar autenticação é um trabalho futuro listado no SDD.

---

## Como Testar

1. Acesse `/admin`
2. Na seção Categorias, clique "+ Nova categoria"
3. Edite o nome diretamente na linha → pressione Enter → observe a sidebar atualizar
4. Clique na célula de cor → escolha uma cor diferente
5. Salve e confirme que a cor aparece na sidebar
6. Crie um atalho vinculado à nova categoria
7. Navegue para `/shortcuts` → confirme que o atalho aparece
8. Exclua a categoria → confirme que os atalhos foram removidos automaticamente

---

## Permissões de Acesso

A rota `/admin` é pública dentro da instância — qualquer usuário na rede com acesso à porta 3000 pode gerenciar categorias e atalhos. Isso é aceitável para uso pessoal/self-hosted em rede doméstica.

**Para uso compartilhado**, recomenda-se adicionar:
- Autenticação básica no Nginx (`auth_basic`)
- Ou guard de rota Vue com token JWT

---

## Estrutura da View

```
Admin.vue
├── Seção Categorias
│   ├── Tabela (thead + tbody rows)
│   │   └── Row → campos inline + color picker + emoji picker
│   └── Botão "+ Nova categoria"
└── Seção Atalhos
    ├── Tabela (thead + tbody rows)
    │   └── Row → campos inline + select de categoria
    └── Botão "+ Novo atalho"
```
