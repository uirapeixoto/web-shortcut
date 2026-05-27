# PR-004 — Biblioteca e Leitor EPUB

**Branch:** `feat/epub-reader`  
**Base:** `main`  
**Status:** Merged  
**Data:** 2026-05  

---

## Resumo

Upload de arquivos `.epub` com armazenamento no servidor, biblioteca com grade de livros e leitor full-screen com navegação por slide horizontal, sumário, controle de fonte, temas claro/escuro, barra de progresso e tratamento robusto de erros.

---

## Motivação

Centralizar a leitura de livros técnicos no mesmo painel de produtividade elimina a necessidade de um leitor EPUB externo. O arquivo fica armazenado no servidor, acessível de qualquer dispositivo na rede local.

---

## Mudanças

### Backend — novos arquivos

| Arquivo | Descrição |
|---|---|
| `backend/routes/ebooks.py` | Upload, listagem, serving e remoção de EPUBs |

### Backend — arquivos modificados

| Arquivo | Mudança |
|---|---|
| `backend/database.py` | Adicionado model `Ebook` + criação do diretório de upload |
| `backend/app.py` | Registro do router de ebooks |
| `backend/requirements.txt` | Adicionado `python-multipart` |

### Frontend — novos arquivos

| Arquivo | Descrição |
|---|---|
| `src/views/Ebooks.vue` | Biblioteca com upload (drag & drop + click), grade de livros |
| `src/components/EpubFlipReader.vue` | Leitor full-screen |

### Frontend — arquivos modificados

| Arquivo | Mudança |
|---|---|
| `src/router/index.js` | Rota `/ebooks` |
| `src/components/SideMenu.vue` | Link "Livros EPUB" na sidebar |
| `frontend/nginx.conf` | `client_max_body_size 100M` para suportar uploads grandes |
| `package.json` | Adicionado `epubjs` |

---

## Arquitetura do Leitor

### Modo de operação epubjs

A URL do arquivo é servida com extensão `.epub` (`/ebooks/{id}/book.epub`). O epubjs detecta a extensão e ativa **archive mode**: baixa o arquivo uma vez, carrega via JSZip e extrai recursos internamente — sem requisições HTTP adicionais por capítulo.

```
URL termina em .epub
  └─ epubjs detecta INPUT_TYPE.EPUB
       └─ archive.open(binaryData) via JSZip
            └─ Todos os recursos lidos do ZIP
```

### Animação de slide

```
Fase 1 (280ms): translateX(-100%)  → página atual sai pela esquerda
Fase 2 (0ms):   translateX(+100%)  → nova página posicionada à direita (sem transição)
Fase 3 (280ms): translateX(0)      → nova página entra pela direita
```

### Timeout e cancelamento

- `Promise.race([rendition.display(), timeout(20s)])` evita loading infinito
- ESC ou botão fechar cancela o processo a qualquer ponto
- Erros exibem overlay com mensagem + botões "Fechar" e "Tentar novamente"

### Progresso de leitura

`book.locations.generate(1024)` roda em background após a primeira página. O evento `locationChanged` atualiza a barra com `percentageFromCfi()`, protegido por `try/catch` para não crashar antes das localizações estarem prontas.

---

## Endpoints Backend

### `POST /ebooks/upload`
- Valida extensão `.epub`
- Salva com nome UUID no disco (`upload/ebook/epub/{uuid}.epub`)
- Insere registro na tabela `ebooks`
- Retorna metadados (id, title, size, created_at)

### `GET /ebooks/{id}/book.epub`
- Serve o arquivo com `Content-Type: application/epub+zip`
- Nome de download: `original_name` do banco

### `DELETE /ebooks/{id}`
- Remove arquivo do disco (se existir)
- Remove registro do banco

---

## Upload via XHR com Progresso

O componente `Ebooks.vue` usa `XMLHttpRequest` (não `fetch`) para ter acesso ao evento `upload.onprogress`:

```javascript
xhr.upload.onprogress = (e) => {
  if (e.lengthComputable)
    uploadProgress.value = Math.round((e.loaded / e.total) * 100)
}
```

---

## Decisões de Design

**Nginx `client_max_body_size 100M`**: O padrão nginx de 1MB bloqueava uploads. Ajustado para 100MB com `proxy_request_buffering off` para streaming direto ao backend sem buffer em memória.

**Arquivo renomeado para UUID**: Evita conflitos de nome e caracteres especiais no filesystem. O nome original é preservado no banco para download/exibição.

**epubjs archive mode via extensão `.epub`**: Tentativas de mode `directory` (HTTP por recurso) falhavam por problemas de namespace XML no OPF. Archive mode é mais confiável e eficiente (1 request vs N).

**`try/catch` em `rendition.next()/prev()`**: Alguns EPUBs têm itens de spine sem entrada correspondente no manifest, causando `new Path(undefined)`. O catch silencioso impede que a UI quebre na navegação.

---

## Como Testar

1. Acesse `/ebooks` pela sidebar ("Livros EPUB")
2. Faça upload de um arquivo `.epub` (drag ou click)
3. Acompanhe a barra de progresso de upload
4. Clique no livro ou no botão "Ler"
5. Navegue com setas, clique nos botões ou use `← →` do teclado
6. Abra o sumário (ícone de lista) e navegue por um capítulo
7. Altere o tamanho da fonte com A+ / A−
8. Alterne tema claro/escuro
9. Pressione ESC — o leitor fecha
10. Exclua um livro — arquivo removido do servidor

---

## Limitações Conhecidas

| Limitação | Causa |
|---|---|
| Scripts do EPUB bloqueados | iframe sandboxed sem `allow-scripts` (segurança intencional) |
| Progresso impreciso em EPUBs longos | `locations.generate` usa heurística de tamanho de texto |
| Capa do livro não exibida | epubjs extração de capa requer parsing adicional do OPF |
| Sem busca no texto | Não suportado no modo archive do epubjs 0.3.x |

---

## Dependências Adicionadas

| Pacote | Versão | Uso |
|---|---|---|
| `epubjs` | ^0.3.93 | Parsing e rendering de EPUBs |
| `python-multipart` | 0.0.9 | Upload multipart/form-data no FastAPI |
