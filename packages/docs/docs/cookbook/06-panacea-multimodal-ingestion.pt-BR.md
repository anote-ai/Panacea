# Panacea Ingestão de Documentos Multi-Modal

Esta receita explica como a Panacea estende a Q&A de documentos + RAG (veja [receita 03](03-panacea-document-qa-rag.md)) além de texto simples para imagens, áudio, vídeo e planilhas — tornando todos eles pesquisáveis através do mesmo pipeline de chunking e embedding.

## O que você vai aprender

- Como a Panacea classifica um upload por tipo MIME e o direciona para um serviço de ingestão dedicado
- Como imagens e quadros de vídeo são transformados em texto indexável usando um LLM com capacidade de visão
- Como o áudio (incluindo a trilha de áudio de um vídeo) é transcrito com o Whisper
- Como planilhas são convertidas em tabelas Markdown em vez de serem achatadas em um despejo de texto não pesquisável
- As flags de recurso e limites de tamanho que governam a ingestão multi-modal

## Por que isso é importante

O Tika (o extrator de texto de documentos padrão) só pode lidar de forma útil com formatos baseados em texto. Sem um tratamento extra, uma imagem, clipe de áudio, vídeo ou planilha carregados falhariam na ingestão ou perderiam toda a sua estrutura. A Panacea, em vez disso, detecta o tipo de mídia no momento do upload e chama um serviço projetado que produz texto limpo, que é então armazenado como `document_text` e flui pelo mesmo caminho de recuperação que qualquer outro documento — assim, uma captura de tela, uma gravação de chamada ou uma planilha de vendas se tornam todas respondíveis através de chat como um PDF.

## Principais arquivos da Panacea

| Arquivo | Por que é importante |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Detecta tipo MIME/extensão no upload e direciona para o serviço de ingestão correto |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — produz uma descrição textual detalhada de uma imagem usando GPT-4o ou Claude vision |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — transcreve áudio com OpenAI Whisper |
| `Panacea/backend/services/video_service.py` | Extrai quadros com `ffmpeg`, descreve cada um com o serviço de visão, transcreve a trilha de áudio e intercala ambos |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — converte CSV/TSV/XLSX/XLS/ODS em tabelas Markdown que preservam cabeçalhos e linhas |
| `Panacea/backend/agents/config.py` | Flags de recurso `AgentConfig`: `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## Como funciona

1. Um arquivo é carregado através do mesmo endpoint usado para documentos regulares; `handler.py` detecta o tipo MIME/extensão para classificá-lo como imagem, vídeo, áudio, tabular ou texto/documento simples.
2. **Imagem** → `vision_service.describe_image()` envia a imagem (codificada em base64) para um modelo com capacidade de visão com um prompt instruindo-o a transcrever qualquer texto visível, descrever gráficos/diagramas/capturas de tela de UI e notar objetos e layout — assim, a descrição sozinha é suficiente para que a busca semântica a encontre mais tarde.
3. **Áudio** → `audio_service.transcribe_audio()` chama o Whisper (`whisper-1`) e retorna uma transcrição com metadados de duração/idioma.
4. **Vídeo** → `video_service` extrai quadros em um intervalo fixo (`VIDEO_FRAME_INTERVAL_SECS`, padrão 30s, limitado a `VIDEO_MAX_FRAMES`) usando `ffmpeg`, descreve cada quadro com o serviço de visão, transcreve a trilha de áudio separadamente e intercala ambos em um documento com timestamp.
5. **Tabular** → `tabular_service.ingest_tabular()` analisa cada planilha nativamente (via `csv`/`pandas`+`openpyxl`/`xlrd`) e a renderiza como uma tabela Markdown, recorrendo ao CSV simples para linhas além das primeiras 500 para que nada seja perdido do índice de busca, mesmo que não seja renderizado de forma agradável.
6. Qualquer texto que sair de qualquer um desses serviços é armazenado como `document_text` e dividido/embutido exatamente como um documento normal, então é recuperável através do fluxo padrão de Q&A RAG da receita 03.

Cada serviço é projetado para **nunca falhar** — uma chamada de visão falhada, uma dependência ausente ou um arquivo muito grande retorna uma string de espaço reservado (por exemplo, `"[Imagem muito grande para análise inline (23.4 MB). Limite: 20 MB.]"`) para que o registro do documento seja sempre criado em vez de falhar todo o upload.

## Execute localmente

A partir da raiz do workspace (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

A ingestão multi-modal está ativada por padrão (`ENABLE_MULTIMODAL=true`). Defina estas variáveis em `backend/.env` para ajustar o comportamento:

```bash
ENABLE_MULTIMODAL=true        # interruptor mestre
MAX_IMAGE_BYTES=20971520      # padrão de 20 MB
MAX_AUDIO_BYTES=26214400      # padrão de 25 MB
MAX_VIDEO_BYTES=524288000     # padrão de 500 MB
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

A ingestão de vídeo requer adicionalmente que o `ffmpeg` esteja presente no `PATH` do contêiner backend (já incluído na imagem Docker fornecida). A ingestão de Excel requer `openpyxl` (XLSX/ODS) e `xlrd` (XLS legado), e ambos os serviços de visão/áudio precisam que `OPENAI_API_KEY` e/ou `ANTHROPIC_API_KEY` sejam definidos dependendo de `DEFAULT_AGENT_MODEL_TYPE`.

### Experimente

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

Então, na interface web em `http://localhost:3000`, abra a mesma sessão de chat e faça uma pergunta sobre a imagem ou planilha que você acabou de carregar — a Panacea responde a partir da descrição/tabela Markdown gerada exatamente como faria a partir de um PDF.

## Notas para o livro de receitas

Esta receita combina bem com a receita 03: é o mesmo pipeline RAG, apenas com um funil mais amplo de formatos de entrada. Vale ressaltar para os leitores que a "qualidade do índice" para imagens/vídeos é apenas tão boa quanto a descrição do modelo de visão, então o ajuste de prompt no `_INDEXING_PROMPT` de `vision_service.py` é um ponto de personalização natural.
