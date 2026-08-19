# PR-007 — Visualizador de Documentação Local

**Branch:** `feat/local-docs-viewer`
**Base:** `main`
**Status:** Em desenvolvimento
**Data:** 2026-08-18

---

## Resumo

Nova funcionalidade "Documentação Local": o usuário cadastra **projetos** apontando para uma pasta na máquina onde o backend roda, navega pela árvore de diretórios daquele projeto e abre qualquer arquivo `.md`/`.markdown` encontrado para **visualizar** (preview renderizado), **editar** (textarea) ou **split** (edição e preview lado a lado) — gravando as alterações diretamente no arquivo original em disco.

Suporta caminhos digitados tanto no formato Windows (`D:\pasta\sub`) quanto Linux/WSL (`/mnt/d/pasta/sub`), árvore de arquivos retrátil, modo de leitura expandido (esconde a árvore para maximizar a área de edição/preview), diagramas Mermaid, citações e highlight de código para C#/.NET, Python, JavaScript, JSON, YAML e SQL.

---

## Motivação

O editor de Markdown existente (`MarkdownEditor.vue`, Ctrl+M) é um bloco de notas único e global, persistido em `localStorage`, sem relação com arquivos reais. Diversos projetos técnicos mantêm documentação em Markdown espalhada em pastas locais; esta feature centraliza a navegação e edição dessa documentação dentro do painel de produtividade, sem precisar abrir um editor de texto ou IDE externo só para consultar/ajustar um `.md`.

---

## Mudanças

### Backend — novos arquivos

| Arquivo | Descrição |
|---|---|
| `backend/routes/projects.py` | CRUD de projetos, árvore de diretórios, leitura/escrita de arquivo `.md` |

### Backend — arquivos modificados

| Arquivo | Mudança |
|---|---|
| `backend/database.py` | Adicionado model `Project` (`name`, `local_path`, `description`, `created_at`) |
| `backend/app.py` | Registro do router de projetos (autenticado, igual aos demais) |

### Frontend — novos arquivos

| Arquivo | Descrição |
|---|---|
| `src/views/Documentation.vue` | Grade de projetos + modal de criação/edição + workspace (árvore + editor) |
| `src/components/DocTreeNode.vue` | Nó recursivo de árvore de diretórios (pastas expansíveis + arquivos `.md`) |
| `src/components/DocMarkdownPanel.vue` | Painel de edição/preview de um arquivo real (3 modos: editar/split/preview), com salvar explícito (botão + Ctrl+S) |

### Frontend — arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/router/index.js` | Rota `/docs` |
| `src/components/SideMenu.vue` | Link "Documentação Local" na sidebar |
| `src/style.css` | Adicionadas classes `.modal-hint` (erro em modais) e `.modal-tip` (dica de formato de caminho) |
| `package.json` | Adicionado `highlight.js` |

---

## Endpoints Backend

| Método | Rota | Descrição |
|---|---|---|
| `POST` | `/projects` | Cria projeto — valida que `local_path` existe e é uma pasta |
| `GET` | `/projects` | Lista projetos |
| `GET` | `/projects/{id}` | Detalhe de um projeto |
| `PUT` | `/projects/{id}` | Edita nome/descrição/caminho |
| `DELETE` | `/projects/{id}` | Remove **apenas o registro** — nunca apaga arquivos do disco |
| `GET` | `/projects/{id}/tree` | Monta árvore recursiva (pastas + arquivos `.md`/`.markdown`), ignorando `.git`, `node_modules`, `__pycache__`, `.venv`, `dist`, `build` e pastas ocultas |
| `GET` | `/projects/{id}/file?path=...` | Lê o conteúdo bruto do arquivo |
| `PUT` | `/projects/{id}/file?path=...` | Sobrescreve o arquivo no disco com o novo conteúdo |

---

## Segurança de Path

Esta é a primeira funcionalidade do projeto que aceita um caminho de sistema de arquivos vindo do cliente — não havia precedente disso no código (uploads de EPUB sempre usam nomes gerados por UUID dentro de uma pasta fixa). Para evitar path traversal e escapes via symlink, todo endpoint que recebe `path` valida com `_resolve_safe_path()` (`backend/routes/projects.py`):

```python
base = os.path.realpath(project.local_path)
target = os.path.realpath(os.path.join(base, rel_path))
if target != base and not target.startswith(base + os.sep):
    raise HTTPException(400, "Caminho inválido")
```

Testado manualmente com `path=../../../etc/passwd` → `400 Caminho inválido`.

Além disso:
- Só arquivos com extensão `.md`/`.markdown` podem ser lidos ou escritos (`400` para qualquer outra extensão).
- Ao criar/editar um projeto, o `local_path` é validado com `os.path.isdir` antes de ser salvo.

---

## Suporte a Caminho Windows (WSL)

Ambiente de desenvolvimento roda em WSL2, onde discos Windows ficam montados em `/mnt/<letra>/...` — um caminho colado do Explorer do Windows (`D:\pasta\sub`) não existe nesse formato para o processo Linux. `_to_fs_path()` (`backend/routes/projects.py`) detecta esse padrão (`X:\...` ou `X:/...`) e traduz para `/mnt/x/...` **apenas no momento de tocar o disco** (`isdir`, montagem de árvore, leitura/escrita de arquivo) — o valor salvo no banco e exibido na UI permanece exatamente como o usuário digitou. A tradução acontece antes de `_resolve_safe_path()`, então a proteção contra path traversal continua válida para os dois formatos.

---

## Renderização: Mermaid, Highlight de Código e Citações

- **Mermaid**: blocos ` ```mermaid ` são detectados no HTML já parseado e renderizados como SVG via `mermaid.render()`, carregado sob demanda (`import('mermaid')`) — já existia no editor original e foi preservado no novo `DocMarkdownPanel.vue`.
- **Highlight de código**: `highlight.js` (core + linguagens individuais) é carregado sob demanda, registrando apenas `csharp`, `python`, `javascript`, `json`, `yaml` e `sql` — mantém o bundle inicial pequeno (cada linguagem vira um chunk separado no build). Aliases comuns (`cs`/`dotnet` → `csharp`, `py` → `python`, `js` → `javascript`, `yml` → `yaml`) são normalizados antes de aplicar o highlight. Tema de cores customizado em `DocMarkdownPanel.vue` para combinar com a paleta dark do app.
- **Citações**: já suportadas nativamente pelo `marked` (GFM); o estilo visual foi refinado (fundo sutil, cantos arredondados, cor diferenciada para blockquotes aninhados).

---

## UX: Árvore Retrátil e Modo de Leitura Expandido

- **Árvore retrátil**: botão no cabeçalho da árvore (`docs-tree-header`) recolhe o painel lateral para uma faixa estreita de 40px (só ícone para reabrir), liberando espaço horizontal sem perder o contexto do projeto ativo.
- **Modo de leitura expandido**: botão no toolbar do editor (`DocMarkdownPanel.vue`) alterna `docs-workspace` para `position: fixed; inset: 0`, ocupando toda a viewport e escondendo a árvore — maximiza a área de edição/split/preview para leitura ou escrita prolongada. Sai do modo com o mesmo botão ou `Esc`.

---

## Decisões de Design

**Edição grava direto no arquivo original**: ao contrário do editor global (que só usa `localStorage`), esta feature é um visualizador/editor de documentação *real* — o botão "Salvar" (e `Ctrl+S`) sobrescreve o `.md` no disco via `PUT /projects/{id}/file`. Por isso o salvamento é deliberado (não há auto-save), com indicador visual de "alterações não salvas" (`dirty` state) para reduzir o risco de perda ou sobrescrita acidental.

**Backend acessa o disco diretamente (modo dev)**: o `docker-compose.yml` atual só monta `data/` e `upload/` como volumes. Esta feature assume que o backend roda com acesso direto ao filesystem do host (modo dev, fora do Docker). Para uso em produção via Docker, será necessário montar a pasta desejada como volume adicional — não foi feito neste PR (ver Limitações Conhecidas).

**`DocMarkdownPanel.vue` como componente irmão, não substituição do `MarkdownEditor.vue`**: a lógica de renderização (`marked` + `mermaid`, toolbar de formatação, 3 modos) foi extraída para um componente reutilizável dirigido por props/emits em vez de `localStorage`, evitando duplicar ~150 linhas de lógica. O `MarkdownEditor.vue` original (bloco de notas global do Ctrl+M) não foi alterado — os dois casos de uso (bloco de notas solto vs. arquivo real de projeto) têm requisitos de persistência diferentes o suficiente para justificar componentes separados.

**Árvore de diretórios construída sob demanda**: `GET /projects/{id}/tree` percorre o disco a cada chamada (sem cache/índice em banco) — simples e sempre consistente com o estado real do filesystem, adequado ao volume esperado (pastas de documentação, não repositórios gigantes).

---

## Como Testar

1. Acesse `/docs` pela sidebar ("Documentação Local").
2. Clique em "+ Novo Projeto", informe um nome, um caminho local válido (ex: a pasta `docs/` deste repositório) e uma descrição.
3. Confirme que o projeto aparece na grade e que o caminho é validado (tente um caminho inexistente — deve bloquear com mensagem de erro).
4. Abra o projeto — a árvore lateral deve exibir apenas pastas e arquivos `.md`.
5. Clique em um arquivo `.md` — o conteúdo deve carregar no painel.
6. Alterne entre os modos "Editar", "Split" e "Preview"; confirme que blocos ` ```mermaid ` renderizam como diagrama no preview.
7. Edite o texto, confirme o indicador de "alterações não salvas", salve (botão ou `Ctrl+S`), e confirme fora da aplicação (ex: `cat arquivo.md`) que o arquivo no disco foi realmente alterado.
8. Tente acessar um `path` fora da pasta do projeto diretamente pela URL da API — deve retornar `400`.
9. Crie um projeto com caminho no formato Windows (ex: `D:\pasta\docs`) — deve validar e funcionar normalmente se a pasta existir no disco montado.
10. Em um arquivo com blocos ` ```csharp `, ` ```python `, ` ```javascript `, ` ```json `, ` ```yaml ` e ` ```sql `, confirme que o preview aplica highlight de sintaxe colorido em cada um.
11. Confirme que uma citação (`> texto`) aparece com fundo destacado e borda lateral no preview.
12. Clique no botão de recolher (◀◀) no cabeçalho da árvore — ela deve encolher para uma faixa estreita; clique novamente para reabrir.
13. Clique no botão de expandir (⛶) no toolbar do editor — a árvore deve desaparecer e o editor ocupar a tela inteira; pressione `Esc` ou clique novamente para sair.
14. Exclua o projeto e confirme que os arquivos originais permanecem intactos no disco.

---

## Limitações Conhecidas

| Limitação | Causa |
|---|---|
| Não funciona em produção via Docker sem ajuste manual | `docker-compose.yml` não monta volumes arbitrários — requer configuração adicional por ambiente |
| Sem detecção de edição concorrente | Se o arquivo for alterado externamente enquanto está aberto no editor, salvar sobrescreve sem aviso |
| Sem backup automático antes de sobrescrever | Edição grava direto no arquivo original, sem cópia de segurança prévia |
| Imagens relativas não são exibidas no preview | `![](./img.png)` não é servido pelo backend — apenas o texto Markdown é renderizado |
| Sem busca em texto | Não é possível buscar por conteúdo dentro dos arquivos do projeto |

---

## Sugestões de Melhoria Futura

1. **Busca em texto** na árvore e no conteúdo dos arquivos do projeto.
2. **Preview de imagens relativas** referenciadas no markdown, via endpoint que sirva arquivos estáticos do projeto (com a mesma validação de path já implementada).
3. **Backup simples antes de sobrescrever** (ex: `.arquivo.md.bak`) para reduzir risco de perda ao editar o arquivo real.
4. **Detecção de alteração externa**: comparar `mtime` do arquivo no momento do carregamento com o momento do salvamento, avisando se houve mudança externa nesse intervalo.
5. **Múltiplas abas** de arquivos abertos simultaneamente no workspace.
6. **Suporte a outros formatos de texto** (`.txt`, `.mdx`) na árvore, não só `.md`/`.markdown`.
7. **Volume Docker configurável** para permitir uso desta funcionalidade em produção (montagem de pasta host via `docker-compose.yml`).
8. **Mais linguagens de highlight** sob demanda (ex: Go, Rust, PHP, Bash) além das 6 já suportadas.
9. **Botão "copiar código"** em cada bloco de código do preview.
10. **Lembrar estado de árvore recolhida/expandida** por projeto (hoje reseta ao trocar de projeto).

---

## Dependências Adicionadas

| Pacote | Versão | Uso |
|---|---|---|
| `highlight.js` | ^11.12.0 | Highlight de sintaxe para C#/.NET, Python, JavaScript, JSON, YAML e SQL no preview |

Reaproveita também `marked` (^18.0.4) e `mermaid` (^11.15.0), já usados por `MarkdownEditor.vue`.
