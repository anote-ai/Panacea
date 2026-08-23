# Änderungsprotokoll

Panacea veröffentlicht noch keine manuell gepflegte Änderungsprotokolldatei — die Quelle der Wahrheit für das, was veröffentlicht wurde, ist:

- **[GitHub Releases](https://github.com/anote-ai/Panacea/releases)** — getaggte Veröffentlichungen für die CLI, die VS Code-Erweiterung und andere Pakete
- **[Commit-Historie](https://github.com/anote-ai/Panacea/commits/main)** — jede Änderung, in chronologischer Reihenfolge

## Erstellen Sie eines für Ihr eigenes Projekt

Die CLI kann ein Änderungsprotokoll aus der Git-Historie für *Ihren* Codebestand schreiben:

```bash
anote changelog                    # seit dem letzten Tag
anote changelog --since v1.2.0
anote changelog --dry-run          # drucken statt CHANGELOG.md zu schreiben
```

Dies schreibt in die eigene `CHANGELOG.md` Ihres Projekts, nicht in die von Panacea.
