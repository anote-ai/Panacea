# Panacea AI Coding Toolchain

Dieses Rezept erklärt, wie Panaceas KI-Coding-Erlebnis über CLI, SDK und VS Code bereitgestellt wird.

## Was Sie lernen werden

- Die verschiedenen Einstiegspunkte für KI-Coding in Panacea
- Wie die CLI, das SDK und die VS Code-Erweiterung mit dem gemeinsamen Backend zusammenhängen
- Wichtige Produktfähigkeiten für private Codeunterstützung
- Wo Sie im Repository nach Implementierungsdetails suchen können

## Warum das wichtig ist

Panacea wurde als ein einheitliches Produkt mit mehreren Schnittstellen entwickelt:

- eine **CLI**, die `anote chat`, Codesuche und Repository-Überprüfung antreibt
- eine **VS Code-Erweiterung** für KI-Unterstützung im Editor
- ein **SDK**, um Panacea in andere Anwendungen einzubetten

Diese Schnittstellen teilen sich ein Backend und eine agentenbasierte Denkebene, was das Produkt über Desktop-, Web- und Code-Workflows hinweg konsistent macht.

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/packages/cli` | TypeScript-CLI-Implementierung für Entwickler-Workflows |
| `Panacea/packages/vscode` | VS Code-Erweiterung und Chat-Integration |
| `Panacea/packages/sdk` | TypeScript-SDK für programmgesteuerten Zugriff |
| `Panacea/packages/backend` | Gemeinsamer Backend-Dienst, der alle UI- und CLI-Interaktionen antreibt |

## Wie es funktioniert

- Eine Benutzeraktion im Coding beginnt an der CLI, dem SDK oder der VS Code-Erweiterung.
- Die Anfrage wird an Panaceas Backend-API gesendet.
- Das Backend verwendet Agentenorchestrierung und Modellanbieter, um codebewusste Antworten zu erzeugen.
- Die Antwort wird in derselben Schnittstelle zurückgegeben, mit Codevorschlägen, Erklärungen oder Korrekturen.

## Nützliche Produktmerkmale

- **CLI**: `anote chat`, Repository-Suche, Code-Überprüfung, Code-Generierung und hilfe durch Embeddings.
- **VS Code**: Inline-Chat, Diff-Vorschauen, Code-Aktionen und Streaming-Antworten.
- **SDK**: ein Client-Wrapper für die Panacea-API, der benutzerdefinierte Integrationen ermöglicht.

## Lokal ausführen

Vom Arbeitsbereichs-Stammverzeichnis (`anote/panacea`):

```bash
cd Panacea
cp packages/backend/.env.example packages/backend/.env
docker compose up --build
```

Dies startet die gemeinsamen Backend- und Frontend-Dienste.

In einem anderen Terminal, führen Sie das CLI-Paket aus:

```bash
cd Panacea/packages/cli
npm install
npm run dev
```

Dann können Sie die CLI lokal verwenden oder mit `npm run build` erstellen.

Für die VS Code-Entwicklung öffnen Sie `Panacea/packages/vscode` in VS Code und starten die Erweiterung mit dem Debugger.

## Hinweise für das Kochbuch

Dieses Rezept ist nützlich für Teamkollegen, die eine hochrangige Einführung in Panaceas KI-Coding-Produkt mit mehreren Schnittstellen benötigen. Es kann auch Leser auf Implementierungsdateien hinweisen, die sie ändern oder erweitern können.
