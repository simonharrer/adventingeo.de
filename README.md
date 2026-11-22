# adventingeo.de – Adventskalender für Kinder

Zwei Online-Adventskalender als Single Page Apps, veröffentlicht mit GitHub Pages unter https://adventingeo.de:

- **Meereszauber** (`/meereszauber/`): 24 Meerestiere mit Weltrekorden und Quizfragen, für 8- bis 9-Jährige
- **Zauber der Tiere** (`/zauber-der-tiere/`): echte Tiere mit Weltrekorden und Fabelwesen im Wechsel, für 6- bis 7-Jährige

## Bedienung

- Im Dezember öffnet sich jeden Tag ein Türchen (Datum des Geräts), im Januar sind noch alle offen.
- `?preview` an der Adresse: alle Türchen lassen sich öffnen (z. B. `https://adventingeo.de/meereszauber/?preview`).
- `?datum=2026-12-07`: tut so, als wäre heute dieses Datum (zum Testen).
- Der Schnee lässt sich unten auf der Seite aus- und einschalten. Geöffnete Türchen und die Schnee-Einstellung merkt sich der Browser.
- Die Türchen sind zufällig, aber bei jedem Besuch gleich angeordnet.

## Aufbau

- `gemeinsam/app.js`, `gemeinsam/styles.css`: der Kalender (für beide gleich)
- `<kalender>/inhalt.js`: Texte, Rekorde, Sagen, Mitmach-Ideen und Quizfragen
- `<kalender>/bilder/`: Bilder (960 px), `klein/` Vorschaubilder, `lizenzen.json` Lizenznachweis, `nachweise.js` Bildnachweise für die Seite

## Bilder und Lizenzen

Alle Bilder stammen von Wikimedia Commons und sind frei (gemeinfrei, CC0, CC BY, CC BY-SA). Übersicht mit Links: [BILDNACHWEISE.md](BILDNACHWEISE.md).
Die Lizenzdaten jedes Bildes zum Zeitpunkt des Downloads (Urheber, Lizenz, Lizenz-URL, Commons-Seite, SHA1 der Originaldatei)
liegen in `<kalender>/bilder/lizenzen.json`.

Bilder ändern: `tools/images.json` anpassen, das alte Bild in `<kalender>/bilder/` löschen, dann

```sh
python3 tools/fetch_final.py   # lädt fehlende Bilder und die Lizenzdaten von Commons
python3 tools/build.py         # erzeugt Vorschaubilder, nachweise.js und BILDNACHWEISE.md
```
