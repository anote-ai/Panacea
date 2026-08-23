# Panacea Dokument Q&A + RAG

Dieses Rezept erklärt, wie Panacea private Dokumentenfragen mit retrieval-augmented generation (RAG) aufbaut.

## Was Sie lernen werden

- Wie Panacea Dokumente aufnimmt und sie als durchsuchbaren Text speichert
- Wie das Backend relevante Teile für eine Frage abruft
- Wie das System Embeddings und Dokumentenquellen verwendet, um Antworten zu untermauern
- Wie Q&A-Feedback erfasst wird und zukünftige Antworten verbessert

## Warum das wichtig ist

Panacea ist so konzipiert, dass Teams Fragen zu privaten Dokumenten stellen können, ohne sie an einen Drittanbieter-Chatdienst zu senden. Der Workflow ist:

1. Dokumente hochladen
2. Inhalte in Teile zerlegen und einbetten
3. Relevante Teile für eine Benutzeranfrage abrufen
4. Antworten mit einem LLM unter Angabe von Quellen erstellen
5. Feedback erfassen, um die Qualität zu verbessern

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/backend/api_endpoints/documents/handler.py` | API-Routen für den Dokumenten-Upload und die -Aufnahme |
| `Panacea/backend/database/db.py` | SQL-Logik für die Dokumentenspeicherung und -abfrage |
| `Panacea/backend/database/qa_feedback.py` | Feedbackerfassung für Dokumenten-Q&A |
| `Panacea/backend/agents/multi_agent_system.py` | Dokumentenabrufagenten, die in Multi-Agenten-Workflows verwendet werden |

## Wie es funktioniert

- Dokumente werden über das Backend hochgeladen und in `documents.document_text` gespeichert.
- Das System zerlegt große Dokumente und erstellt Abrufmetadaten für eine schnelle Suche.
- Wenn ein Benutzer eine Frage stellt, wählt Panacea einen oder mehrere spezialisierte Agenten aus, um die besten Teile abzurufen und dann eine Antwort zu generieren.
- Das Ergebnis enthält Quellenangaben, sodass Benutzer die Antwort auf das ursprüngliche Dokument zurückverfolgen können.
- Feedbacksignale werden in `qa_feedback` protokolliert, um zukünftige Qualitätsverbesserungen zu ermöglichen.

## Lokal ausführen

Vom Arbeitsbereichs-Stammverzeichnis (`anote/panacea`):

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Dies startet das Backend, die Webanwendung, MySQL, Redis und Tika.

Wenn Sie sich bereits im Rezeptordner befinden, verwenden Sie:

```bash
cd ../../../Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

Öffnen Sie `http://localhost:3000`, um die Panacea-Web-UI zu verwenden. Dokumenten-Uploads werden über die Backend-Route `POST /ingest-pdf` mit den erforderlichen Formularfeldern `chat_id` und `files[]` verarbeitet.

Beispiel für einen Upload-Befehl:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./path/to/document.pdf"
```

### Minimaler Upload-Walkthrough

1. Starten Sie Panacea vom Repo-Stammverzeichnis:

```bash
cd Panacea
cp backend/.env.example backend/.env
docker compose up --build
```

2. Laden Sie in einem anderen Terminal ein einzelnes Text- oder PDF-Dokument hoch:

```bash
curl -X POST http://localhost:5000/ingest-pdf \
  -F chat_id=1 \
  -F "files[]=@./Cookbook/recipes/03-panacea-document-qa-rag/data/sample-doc.txt"
```

3. Bestätigen Sie, dass das Backend eine erfolgreiche `Document Uploaded`-Antwort zurückgibt.

4. Verwenden Sie die Web-UI unter `http://localhost:3000` und wählen Sie dieselbe Chatsitzung aus, um Fragen zu dem hochgeladenen Dokument zu stellen.

Wenn Sie die API direkt nach dem Upload testen möchten, finden Sie die Chatsitzungs-ID in der UI oder der Datenbank und senden Sie Fragen über den Chatfluss der App. Panacea wird relevante Teile abrufen und eine fundierte Antwort generieren.

## Hinweise für das Kochbuch

Dieses Rezept eignet sich ideal für einen Eintrag im Kochbuch, der erklärt, wie Panacea private Wissensarbeit unterstützt. Es ist konzeptioneller als ein einzeiliger Skript, da der wahre Wert im Verständnis der Dokumentenaufnahme- und Abrufarchitektur liegt.
