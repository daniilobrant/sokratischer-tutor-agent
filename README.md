# Sokratischer Tutor für Codex

[🇩🇪 Deutsch](#-deutsch) | [🇬🇧 English](#-english)

**[Live-Demo / Live demo](https://daniilobrant.github.io/sokratischer-tutor-agent/)**

## 🇩🇪 Deutsch

Ein Lernbegleiter, der Vorlesungsstoff mithilfe von Codex, Fragen und nachvollziehbaren Quellen erschließt.

### Funktionen

- Markdown-, Text- und JSON-Dateien bis 2 MB importieren und nach Textstellen mit Zeilennummer suchen.
- Themen und Lernstand festhalten; Codex stellt Verständnisfragen und gibt Hinweise.
- Die öffentliche Demo speichert Daten im Browser. Für ein echtes Tutorengespräch das Projekt lokal in Codex öffnen.

### Architektur und Datenschutz

Codex führt den Dialog. Ein Python-Werkzeug verwaltet Quellen und Lernstand lokal in SQLite; die Suche ist regelbasiert und verwendet kein Sprachmodell. Das lokale Cockpit verwendet einen Python-Server auf 127.0.0.1. GitHub Pages stellt eine eigenständige Browser-Demo mit localStorage bereit. **Beide Speicher sind getrennt** und werden nicht automatisch synchronisiert. Importierte Texte sind Daten, keine Anweisungen. Es sind keine API-Schlüssel eingebettet; für Codex gelten deine Zugangsvoraussetzungen und Nutzungsgrenzen.

### Lokal starten

1. Repository herunterladen und den Ordner in Codex öffnen.
2. Im Ordner den folgenden Befehl ausführen und http://127.0.0.1:8765/ öffnen:

       python3 tutor_tools.py serve

3. Unterlagen importieren und Codex bitten: „Hilf mir, dieses Thema mit Fragen zu verstehen.“

Alternativ Dateien mit dem Befehl python3 tutor_tools.py import gefolgt vom Dateipfad importieren. PDF- und Word-Dokumente vorher als Text exportieren. Python 3 ist erforderlich; zusätzliche Python-Pakete sind nicht nötig. Die Pages-Demo ist eine Website, keine installierbare PWA und kein Server für Codex.

### Daten, Lizenz und Quellen

Die lokale Datei data/tutor.sqlite3 ist von Git ausgeschlossen und enthält importierte Dokumente und Lernstände. Eine automatische Sicherung oder geräteübergreifende Synchronisierung gibt es nicht. Für dieses Projekt ist keine separate Lizenz angegeben. Entstanden im Rahmen der Vorlesung „Data Science & KI“ bei Prof. Dr. Mathias Engel; [Kursmaterial](https://github.com/ProfEngel/KI-Literacy) und [Trinity-Referenz](https://profengel.github.io/KI-Literacy/trinity-agenten.html).

## 🇬🇧 English

A study companion that uses Codex, questions and traceable source passages to explore course material.

### Features

- Import Markdown, text and JSON files up to 2 MB and search for passages with line numbers.
- Record topics and learning progress; Codex asks questions and provides hints.
- The public demo stores data in your browser. Open the project locally in Codex for an actual tutoring conversation.

### Architecture and privacy

Codex handles the conversation. A Python tool manages sources and progress locally in SQLite; search is deterministic and does not use a language model. The local cockpit uses a Python server bound to 127.0.0.1. GitHub Pages serves a separate browser demo using localStorage. **The two stores are separate** and do not sync automatically. Imported text is treated as data, not instructions. No API keys are embedded; Codex access is subject to applicable terms and limits.

### Quick start

1. Download the repository and open its folder in Codex.
2. Run the following command in the folder and open http://127.0.0.1:8765/:

       python3 tutor_tools.py serve

3. Import your material and ask Codex to guide you through a topic with questions.

Alternatively import a file using python3 tutor_tools.py import followed by its path. Export PDF and Word files to text first. Python 3 is required; no additional Python packages are needed. The Pages demo is a website, not an installable PWA or a Codex server.

### Data, license and sources

The local data/tutor.sqlite3 database is excluded from Git and contains imported documents and progress. There is no automatic backup or cross-device sync. No separate license has been specified for this project. Created as coursework for “Data Science & AI” with Prof. Dr. Mathias Engel; [course materials](https://github.com/ProfEngel/KI-Literacy) and [Trinity reference](https://profengel.github.io/KI-Literacy/trinity-agenten.html).
