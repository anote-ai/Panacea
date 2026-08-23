# Schnellstart

## 1. Initialisieren

```bash
anote init
```

Dies führt Sie durch die Einrichtung Ihres API-Schlüssels und des bevorzugten LLM-Anbieters.

## 2. Stellen Sie eine Frage

```bash
# Allgemeine Frage
anote ask "wie funktioniert die Authentifizierung in diesem Code-Repository?"

# Fokus auf eine Datei
anote ask --file src/auth.ts "erkläre das"

# Code pipen
cat src/handler.py | anote ask "was könnte hier schiefgehen?"
```

## 3. Fehler automatisch beheben

```bash
# Beheben und iterieren, bis die Tests bestehen (bis zu 5 Runden)
anote fix --loop --max-iterations 5
```

## 4. Indizieren für semantische Suche

```bash
# Indizieren Sie Ihr Code-Repository (einmal ausführen, dann aktuell halten)
anote index

# Semantisch suchen
anote search "JWT-Token-Validierung"
anote search "Datenbankverbindungspool"
```

## 5. Überprüfen Sie einen PR

```bash
anote review --pr 42
```

## 6. Generieren Sie ein Änderungsprotokoll

```bash
anote changelog --since v1.2.0
```
