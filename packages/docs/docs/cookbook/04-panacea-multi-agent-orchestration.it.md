# Panacea Multi-Agent Orchestration

Questa ricetta spiega l'architettura di orchestrazione degli agenti di Panacea: come l'orchestratore assegna compiti, sceglie agenti e supporta flussi di lavoro sequenziali e gerarchici.

## Cosa imparerai

- Il ruolo dell'orchestratore come cervello del sistema
- Come Panacea instrada i compiti agli agenti specializzati
- La differenza tra flussi di lavoro sequenziali e gerarchici
- Come le squadre di agenti collaborano per un obiettivo comune
- Come funziona la registrazione degli strumenti affinché gli agenti possano utilizzare nuove capacità

## Perché è importante

In Panacea, l'orchestratore non è casuale. Sceglie il miglior agente in base alle descrizioni delle capacità, al contesto del compito e allo stato del flusso di lavoro. Questo rende il sistema prevedibile ed estensibile.

## Concetti chiave

- **Orchestratore** — coordinatore centrale che decide quale agente eseguire successivamente
- **Agente** — unità autonoma con uno scopo definito, come `DocumentRetrievalAgent`, `GeneralKnowledgeAgent` o `ChatHistoryAgent`
- **Squadra** — un gruppo di agenti che lavorano insieme verso un obiettivo comune
- **Flussi di lavoro** — lo stile di collaborazione; possono essere:
  - **Sequenziale**: un passo segue l'altro in ordine
  - **Gerarchico**: una catena di comando in cui l'orchestratore delega sottocompiti a specialisti
- **Strumenti** — funzioni che gli agenti possono chiamare per eseguire azioni come cercare, caricare o eseguire codice

## File chiave di Panacea

| File | Perché è importante |
|---|---|
| `Panacea/backend/agents/multi_agent_system.py` | Logica di orchestrazione e instradamento dei flussi di lavoro |
| `Panacea/backend/agents/autonomous_agent.py` | Registrazione degli strumenti e ciclo di vita dell'agente |
| `Panacea/backend/agents/routing.py` | Logica di supporto per l'instradamento dei compiti |
| `Panacea/backend/agents/reactive_agent.py` | Inizializza il sistema multi-agente e lo collega ai flussi di chat |

## Come funziona

1. Un utente invia un compito o una query.
2. L'agente orchestratore esamina l'input e sceglie un agente successivo in base alle capacità e ai requisiti del compito.
3. Gli agenti specializzati eseguono la loro parte della pipeline e possono restituire risultati intermedi.
4. L'orchestratore può continuare in modo sequenziale o continuare a delegare sottocompiti in un modello gerarchico.
5. Il risultato finale viene assemblato e restituito all'utente.

### Flusso di lavoro sequenziale

Un flusso di lavoro sequenziale è utile per pipeline fisse come:

- recuperare frammenti di documenti → riassumere → rispondere all'utente
- raccogliere contesto del codice → analizzare il codice → restituire suggerimenti di revisione

Ogni passo viene eseguito in ordine e il passo successivo utilizza l'output del passo precedente.

### Flusso di lavoro gerarchico

Un flusso di lavoro gerarchico è utile per compiti complessi in cui l'orchestratore gestisce specialisti:

- l'orchestratore assegna un agente per raccogliere dati
- un altro agente convalida i dati
- un terzo agente genera la risposta finale

Questo è simile a una catena di comando: l'orchestratore rimane in controllo e delega il lavoro agli agenti esperti.

## Registrazione degli strumenti

Panacea supporta la registrazione dinamica degli strumenti. Se un agente ha bisogno di una nuova capacità, può chiamare `register_tool(...)` da `backend/agents/autonomous_agent.py`.

Ciò significa che il ricettario può documentare non solo come utilizzare gli strumenti esistenti, ma anche come aggiungere nuovi strumenti al sistema.

## Ciclo di feedback

Il feedback degli utenti è essenziale per migliorare la selezione degli agenti. Panacea registra il feedback dalle domande e risposte sui documenti e dai risultati dei compiti affinché l'orchestratore possa apprendere quali agenti e strumenti producono i migliori risultati.

## Note per il ricettario

Questa ricetta è un forte candidato per una spiegazione manuale. Dovrebbe includere diagrammi o esempi di flusso passo-passo che mostrano perché l'orchestratore prende decisioni invece di lasciare la selezione degli agenti al caso.
