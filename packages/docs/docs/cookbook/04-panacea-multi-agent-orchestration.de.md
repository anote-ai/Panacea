# Panacea Multi-Agent Orchestrierung

Dieses Rezept erklärt die Agenten-Orchestrierungsarchitektur von Panacea: wie der Orchestrator Aufgaben zuweist, Agenten auswählt und sequenzielle sowie hierarchische Workflows unterstützt.

## Was Sie lernen werden

- Die Rolle des Orchestrators als das Gehirn des Systems
- Wie Panacea Aufgaben an spezialisierte Agenten weiterleitet
- Der Unterschied zwischen sequenziellen und hierarchischen Workflows
- Wie Gruppen von Agenten an einem gemeinsamen Ziel zusammenarbeiten
- Wie die Registrierung von Werkzeugen funktioniert, damit Agenten neue Fähigkeiten nutzen können

## Warum das wichtig ist

In Panacea ist der Orchestrator nicht zufällig. Er wählt den besten Agenten basierend auf Fähigkeitsbeschreibungen, Aufgaben-Kontext und Workflow-Zustand. Das macht das System vorhersehbar und erweiterbar.

## Schlüsselkonzepte

- **Orchestrator** — zentraler Koordinator, der entscheidet, welcher Agent als nächstes ausgeführt wird
- **Agent** — autonome Einheit mit einem definierten Zweck, wie `DocumentRetrievalAgent`, `GeneralKnowledgeAgent` oder `ChatHistoryAgent`
- **Crew** — eine Gruppe von Agenten, die zusammen auf ein gemeinsames Ziel hinarbeiten
- **Workflows** — der Kollaborationsstil; kann sein:
  - **Sequenziell**: ein Schritt folgt dem anderen in der Reihenfolge
  - **Hierarchisch**: eine Befehlskette, in der der Orchestrator Teilaufgaben an Spezialisten delegiert
- **Werkzeuge** — Funktionen, die Agenten aufrufen können, um Aktionen wie Suchen, Hochladen oder Ausführen von Code durchzuführen

## Wichtige Panacea-Dateien

| Datei | Warum es wichtig ist |
|---|---|
| `Panacea/backend/agents/multi_agent_system.py` | Orchestrator- und Workflow-Routing-Logik |
| `Panacea/backend/agents/autonomous_agent.py` | Werkzeugregistrierung und Agentenlebenszyklus |
| `Panacea/backend/agents/routing.py` | Hilfslogik für das Aufgaben-Routing |
| `Panacea/backend/agents/reactive_agent.py` | Initialisiert das Multi-Agenten-System und verbindet es mit Chat-Flows |

## Wie es funktioniert

1. Ein Benutzer reicht eine Aufgabe oder Anfrage ein.
2. Der Orchestrator-Agent überprüft die Eingabe und wählt einen nächsten Agenten basierend auf Fähigkeiten und Anforderungen der Aufgabe aus.
3. Spezialisierte Agenten führen ihren Teil der Pipeline aus und können Zwischenresultate zurückgeben.
4. Der Orchestrator kann entweder sequenziell fortfahren oder weiterhin Teilaufgaben in einem hierarchischen Muster delegieren.
5. Das endgültige Ergebnis wird zusammengestellt und dem Benutzer zurückgegeben.

### Sequenzieller Workflow

Ein sequenzieller Workflow ist nützlich für feste Pipelines wie:

- Dokumentenabschnitte abrufen → zusammenfassen → Benutzer antworten
- Code-Kontext sammeln → Code analysieren → Überprüfungsvorschläge zurückgeben

Jeder Schritt wird in der Reihenfolge ausgeführt, und der nächste Schritt verwendet die Ausgabe des vorherigen Schrittes.

### Hierarchischer Workflow

Ein hierarchischer Workflow ist nützlich für komplexe Aufgaben, bei denen der Orchestrator Spezialisten verwaltet:

- Orchestrator weist einem Agenten zu, Daten zu sammeln
- Ein anderer Agent validiert die Daten
- Ein dritter Agent generiert die endgültige Antwort

Dies ähnelt einer Befehlskette: Der Orchestrator bleibt in Kontrolle und delegiert die Arbeit an Fachagenten.

## Werkzeugregistrierung

Panacea unterstützt die dynamische Werkzeugregistrierung. Wenn ein Agent eine neue Fähigkeit benötigt, kann er `register_tool(...)` aus `backend/agents/autonomous_agent.py` aufrufen.

Das bedeutet, dass das Kochbuch nicht nur dokumentieren kann, wie man bestehende Werkzeuge verwendet, sondern auch, wie man neue Werkzeuge in das System hinzufügt.

## Feedback-Schleife

Benutzerfeedback ist entscheidend für die Verbesserung der Agentenauswahl. Panacea protokolliert Feedback aus Dokumenten-Q&A und Aufgabenergebnissen, damit der Orchestrator lernen kann, welche Agenten und Werkzeuge die besten Ergebnisse liefern.

## Hinweise für das Kochbuch

Dieses Rezept ist ein starker Kandidat für eine manuelle Erklärung. Es sollte Diagramme oder Schritt-für-Schritt-Flussbeispiele enthalten, die zeigen, warum der Orchestrator Entscheidungen trifft, anstatt die Agentenauswahl dem Zufall zu überlassen.
