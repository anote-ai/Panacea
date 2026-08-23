# Ingestion de Documents Multi-Modal de Panacea

Cette recette explique comment Panacea étend la Q&A de documents + RAG (voir [recette 03](03-panacea-document-qa-rag.md)) au-delà du texte brut pour inclure des images, de l'audio, de la vidéo et des tableurs — rendant tous ces formats recherchables via le même pipeline de découpage et d'intégration.

## Ce que vous apprendrez

- Comment Panacea classe un téléchargement par type MIME et le dirige vers un service d'ingestion dédié
- Comment les images et les images vidéo sont transformées en texte indexable à l'aide d'un LLM capable de vision
- Comment l'audio (y compris la piste audio d'une vidéo) est transcrit avec Whisper
- Comment les tableurs sont convertis en tables Markdown au lieu d'être aplatis en un texte non recherchable
- Les drapeaux de fonctionnalités et les limites de taille qui régissent l'ingestion multi-modale

## Pourquoi cela importe

Tika (l'extracteur de texte par défaut) ne peut traiter utilement que les formats basés sur du texte. Sans traitement supplémentaire, une image, un clip audio, une vidéo ou un tableur téléchargé échouerait à s'ingérer ou perdrait toute sa structure. Panacea détecte plutôt le type de média au moment du téléchargement et appelle un service spécialement conçu qui produit un texte propre, qui est ensuite stocké comme `document_text` et suit exactement le même chemin de récupération que tout autre document — ainsi, une capture d'écran, un enregistrement d'appel ou un tableur de ventes deviennent tous répondables via le chat comme un PDF le serait.

## Fichiers clés de Panacea

| Fichier | Pourquoi cela importe |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | Détecte le type MIME/l'extension lors du téléchargement et dirige vers le bon service d'ingestion |
| `Panacea/backend/services/vision_service.py` | `describe_image()` — produit une description textuelle détaillée d'une image à l'aide de GPT-4o ou de la vision de Claude |
| `Panacea/backend/services/audio_service.py` | `transcribe_audio()` — transcrit l'audio avec OpenAI Whisper |
| `Panacea/backend/services/video_service.py` | Extrait des images avec `ffmpeg`, décrit chacune avec le service de vision, transcrit la piste audio et entrelace les deux |
| `Panacea/backend/services/tabular_service.py` | `ingest_tabular()` — convertit CSV/TSV/XLSX/XLS/ODS en tables Markdown qui préservent les en-têtes et les lignes |
| `Panacea/backend/agents/config.py` | Drapeaux de fonctionnalités `AgentConfig` : `ENABLE_MULTIMODAL`, `MAX_IMAGE_BYTES`, `MAX_AUDIO_BYTES`, `MAX_VIDEO_BYTES`, `VIDEO_FRAME_INTERVAL_SECS`, `VIDEO_MAX_FRAMES` |

## Comment cela fonctionne

1. Un fichier est téléchargé via le même point de terminaison utilisé pour les documents réguliers ; `handler.py` détecte le type MIME/l'extension pour le classer comme image, vidéo, audio, tabulaire ou texte/document brut.
2. **Image** → `vision_service.describe_image()` envoie l'image (encodée en base64) à un modèle capable de vision avec une invite lui demandant de transcrire tout texte visible, de décrire des graphiques/diagrammes/captures d'écran d'interface utilisateur, et de noter les objets et la mise en page — ainsi, la description seule est suffisante pour que la recherche sémantique puisse la retrouver plus tard.
3. **Audio** → `audio_service.transcribe_audio()` appelle Whisper (`whisper-1`) et retourne une transcription avec des métadonnées de durée/langue.
4. **Vidéo** → `video_service` extrait des images à un intervalle fixe (`VIDEO_FRAME_INTERVAL_SECS`, par défaut 30s, limité à `VIDEO_MAX_FRAMES`) à l'aide de `ffmpeg`, décrit chaque image avec le service de vision, transcrit la piste audio séparément, et entrelace les deux dans un document horodaté.
5. **Tabulaire** → `tabular_service.ingest_tabular()` analyse chaque feuille nativement (via `csv`/`pandas`+`openpyxl`/`xlrd`) et la rend sous forme de table Markdown, revenant à un CSV brut pour les lignes au-delà des 500 premières afin que rien ne soit perdu de l'index de recherche même si cela n'est pas rendu joliment.
6. Quel que soit le texte provenant de l'un de ces services, il est stocké comme `document_text` et découpé/intégré exactement comme un document normal, de sorte qu'il soit récupérable via le flux standard de Q&A RAG de la recette 03.

Chaque service est conçu pour **ne jamais lever** — un appel de vision échoué, une dépendance manquante ou un fichier trop volumineux retourne une chaîne de remplacement (par exemple, `"[Image too large for inline analysis (23.4 MB). Limit: 20 MB.]"`) afin que l'enregistrement du document soit toujours créé au lieu d'échouer lors du téléchargement complet.

## Exécutez-le localement

Depuis la racine de l'espace de travail (`anote/panacea`) :

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

L'ingestion multi-modale est activée par défaut (`ENABLE_MULTIMODAL=true`). Définissez ces valeurs dans `backend/.env` pour ajuster le comportement :

```bash
ENABLE_MULTIMODAL=true        # interrupteur principal
MAX_IMAGE_BYTES=20971520      # 20 Mo par défaut
MAX_AUDIO_BYTES=26214400      # 25 Mo par défaut
MAX_VIDEO_BYTES=524288000     # 500 Mo par défaut
VIDEO_FRAME_INTERVAL_SECS=30
VIDEO_MAX_FRAMES=20
```

L'ingestion vidéo nécessite également que `ffmpeg` soit présent dans le `PATH` du conteneur backend (déjà inclus dans l'image Docker fournie). L'ingestion Excel nécessite `openpyxl` (XLSX/ODS) et `xlrd` (XLS hérité), et les deux services de vision/audio ont besoin de `OPENAI_API_KEY` et/ou `ANTHROPIC_API_KEY` définis en fonction de `DEFAULT_AGENT_MODEL_TYPE`.

### Essayez-le

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./screenshot.png"

curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./quarterly_sales.xlsx"
```

Ensuite, dans l'interface web à `http://localhost:3000`, ouvrez la même session de chat et posez une question sur l'image ou le tableur que vous venez de télécharger — Panacea répond à partir de la description générée/table Markdown exactement comme il le ferait à partir d'un PDF.

## Notes pour le livre de recettes

Cette recette s'associe bien avec la recette 03 : c'est le même pipeline RAG, juste avec un entonnoir d'entrées plus large. Il vaut la peine de signaler aux lecteurs que la "qualité de l'index" pour les images/vidéos est seulement aussi bonne que la description du modèle de vision, donc le réglage des invites dans `_INDEXING_PROMPT` de `vision_service.py` est un point de personnalisation naturel.
