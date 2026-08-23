# Sitzungen verwalten

Jede `anote chat`-Unterhaltung wird lokal als Sitzung gespeichert — ihre Nachrichten, Token-Nutzung und Arbeitsverzeichnis.

## Sitzungen auflisten

```bash
anote sessions list
anote sessions ls --limit 50
```

```
Gespeicherte Sitzungen (3):
  a1b2c3d4  12 msgs  in=4,200 out=1,800  vor 10m  /Users/you/project
  e5f6a7b8  4 msgs   in=900 out=400      vor 2h   /Users/you/other-project
```

## Eine Sitzung anzeigen

```bash
anote sessions show a1b2c3d4
anote sessions show a1b2c3d4 --limit 50   # mehr Nachrichtenverlauf
```

Druckt die Unterhaltung, Token-Gesamtsummen und das Arbeitsverzeichnis für diese Sitzung. Sie können ein kurzes Präfix der Sitzungs-ID anstelle der vollständigen ID übergeben.

## Eine Sitzung löschen

```bash
anote sessions delete a1b2c3d4
anote sessions rm a1b2c3d4
```

## Nächste Schritte

- [Häufige Arbeitsabläufe](common-workflows.md)
- [Wie Panacea funktioniert](../core-concepts/how-it-works.md) — Züge, Kompaktierung und wie die Sitzungsdauer den Kontext beeinflusst
