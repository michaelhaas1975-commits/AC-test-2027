# Lern-Apps auf GitHub: Anleitung für Claude

Diese Anleitung gehört in die Projektanweisungen. Sie beschreibt, wie in diesem Projekt neue Übungstests (Multiple Choice, Aussagenpaare, Zahleneingabe) als iPad-taugliche Lern-App hinterlegt und über GitHub Pages veröffentlicht werden.

## Projektspezifische Angaben

Vor dem ersten Einsatz in einem Projekt ausfüllen:

- **Projektordner:** `PROJEKTNAME` (Kleinbuchstaben, Ziffern, Bindestrich; zum Beispiel `abitur-mathe`)
- **Apps in diesem Projekt:** zum Beispiel `analysis`, `stochastik`
- **Zielgruppe und Niveau:** zum Beispiel „Abitur Hessen, Leistungskurs, Q3/Q4“
- **Zeitvorgabe je Test:** zum Beispiel 30 Minuten, oder 0 für ohne Zeitlimit

## Wo alles liegt

- Repository: `michaelhaas1975-commits/AC-test-2027` (öffentlich)
- Veröffentlichte Seiten: `https://michaelhaas1975-commits.github.io/AC-test-2027/`
- Ein Projekt mit dem Zielordner `abitur-mathe` erscheint unter `https://michaelhaas1975-commits.github.io/AC-test-2027/abitur-mathe/`

Aufbau des Repositorys:

```
index.html, quantitativ.html, …        AC-Training (Projekt „ac“, liegt im Wurzelordner)
<zielordner>/index.html, <app>.html     gebaute Seiten weiterer Projekte (nie von Hand bearbeiten)
_quellen/werkzeug/template.html         App-Vorlage für alle Projekte
_quellen/werkzeug/build.py              baut und prüft alle Apps
_quellen/werkzeug/beispiel/             vollständiges Beispielprojekt zum Kopieren
_quellen/<projekt>/projekt.json         Titel, Zielordner, Liste der Apps
_quellen/<projekt>/<app>/data.json      Tests und Aufgaben einer App
_quellen/<projekt>/<app>/img/           Bilder zu den Aufgaben (optional)
```

Ordner, die mit einem Unterstrich beginnen, veröffentlicht GitHub Pages nicht. Die Quellen sind im Repository trotzdem öffentlich lesbar.

## Voraussetzungen in der Sitzung

1. Die Sitzung braucht eine Kommandozeile und Zugriff auf GitHub. Repository mit Schreibrecht anhängen (Werkzeug zum Hinzufügen eines Repositorys, Zugriff „push“), dann klonen:
   ```
   git clone --depth 1 https://github.com/michaelhaas1975-commits/AC-test-2027 ~/lernapps
   ```
2. Vor dem ersten Schreiben prüfen, ob ein Push möglich ist. Wird er abgelehnt, fehlt die Freigabe der Claude-GitHub-App für dieses Repository. Das dem Nutzer klar sagen; er muss sie unter github.com in den Einstellungen der Claude-App erteilen.
3. Fehlen Kommandozeile oder GitHub-Zugriff ganz, die Aufgaben trotzdem vollständig als `data.json` erstellen, als Datei übergeben und sagen, dass das Veröffentlichen eine Sitzung mit GitHub-Zugriff braucht.
4. GitHub Pages ist für das Repository bereits eingeschaltet. Claude kann diese Einstellung nicht selbst ändern und muss es auch nicht.

## Arbeitsablauf

**Neuen Test zu einer bestehenden App hinzufügen**

1. `_quellen/<projekt>/<app>/data.json` lesen und das Niveau der vorhandenen Tests ansehen.
2. Den neuen Test **ans Ende** der Liste `tests` anhängen.
3. Bauen und prüfen (siehe unten), dann committen und pushen.

**Neues Projekt anlegen**

1. `_quellen/werkzeug/beispiel/` nach `_quellen/<projekt>/` kopieren.
2. In `projekt.json` Titel, Beschreibung, `ziel` (= Projektordner) und die Apps eintragen. App-Ordner entsprechend umbenennen.
3. In jeder `data.json` einen eindeutigen `key` setzen, immer mit dem Projektnamen als Präfix: `abitur-mathe-analysis`.
4. Tests erstellen, bauen, prüfen, pushen.

**Bauen und hochladen**

```
cd ~/lernapps
python3 _quellen/werkzeug/build.py --check      # nur prüfen
python3 _quellen/werkzeug/build.py <projekt>    # prüft alles, baut nur dieses Projekt
git add -A
git commit -m "<projekt>: Test 3 in <app> ergänzt"
git pull --rebase origin main
git push origin main
```

Nach dem Push braucht GitHub Pages ein bis zwei Minuten. Dem Nutzer am Ende die Adresse der Projektseite nennen. Der Sandbox-Proxy lässt `github.io` in der Regel nicht zu; die Seite lässt sich von hier aus also nicht aufrufen. Das offen sagen.

## Regeln, die nichts kaputt machen

- **Tests nie umsortieren, löschen oder umbenennen.** Die App speichert Ergebnisse im Browser nach der Position des Tests. Neue Tests nur anhängen. Ist eine Korrektur einer Aufgabe nötig, nur deren Text, Optionen oder Lösung ändern, nicht die Reihenfolge.
- **`key` nie ändern** und nie doppelt vergeben. Alle Projekte teilen sich eine Webadresse und damit einen Browserspeicher; `build.py` bricht bei doppelten Schlüsseln ab.
- **Dateinamen der Apps (`datei` in projekt.json) nie ändern.** Auf dem iPad gespeicherte Lesezeichen verweisen darauf.
- **Andere Projekte nicht anfassen**, insbesondere nicht `_quellen/ac/` und die Dateien im Wurzelordner.
- **Gebaute HTML-Dateien nie von Hand bearbeiten.** Immer die Quellen ändern und neu bauen.
- **Keine personenbezogenen Daten** in Aufgaben, Titeln oder Beschreibungen. Das Repository ist öffentlich.

## Datenformat

### projekt.json

```json
{
  "titel": "Abitur Mathematik",
  "eyebrow": "Abiturvorbereitung · Training",
  "ueberschrift": "Übungstests",
  "beschreibung": "Zwei Apps mit Übungstests, Timer und Auswertung.",
  "ziel": "abitur-mathe",
  "app_defaults": {
    "eyebrow": "Abiturvorbereitung · Training",
    "rules_title": "So funktioniert die App",
    "rules": ["Gezählt wird die zuletzt angetippte Antwort.", "Mit „Markieren“ kennzeichnest du Aufgaben für den zweiten Durchgang."]
  },
  "apps": [
    {"ordner": "analysis", "datei": "analysis.html", "app_titel": "Abitur Analysis", "untertitel": "15 Aufgaben je Test · 30 Minuten"}
  ]
}
```

`app_defaults` gilt für alle Apps des Projekts, sofern die `data.json` die Felder nicht selbst setzt. Ohne `rules` zeigt die App die Hinweise des AC-Trainings; für andere Projekte deshalb immer eigene `rules` angeben.

### data.json

```json
{
  "key": "abitur-mathe-analysis",
  "label": "Analysis",
  "description": "Vier Übungstests zu Ableitung, Integral und Kurvendiskussion.",
  "tests": [
    {"name": "Übungstest 1", "level": "Grundlagen", "minutes": 30, "intro": null, "items": [ … ]}
  ]
}
```

- `minutes`: ganze Zahl; 0 bedeutet ohne Zeitlimit.
- `items`: beliebig viele Aufgaben, `num` von 1 an fortlaufend. 15 Aufgaben je Test haben sich bewährt.

### Projekte mit Fächerebene (`faecher`)

Statt einer flachen Liste `apps` kann `projekt.json` eine Liste `faecher` enthalten. Dann entsteht eine Startseite mit Fachwahl und je Fach eine eigene Übersicht mit Zurück-Link. Beispiel: `_quellen/bns/projekt.json`.

```json
"faecher": [
  {"ordner": "geschichte", "titel": "Geschichte", "untertitel": "…", "beschreibung": "…",
   "apps": [
     {"ordner": "tests", "datei": "tests.html", "karte": "Tests", "untertitel": "…"},
     {"ordner": "trainer", "datei": "lerntrainer.html", "typ": "trainer", "karte": "Lerntrainer", "untertitel": "…"}
   ]}
]
```

Quellen liegen unter `_quellen/<projekt>/<fach>/<app>/data.json`, gebaut wird nach `<ziel>/<fach>/<datei>`. `karte` ist der Text auf der Übersichtskarte (sonst `label`). Neue Fächer nur **anhängen**, Ordner- und Dateinamen nie ändern.

### Lerntrainer (`"typ": "trainer"`)

Spielerische App mit Missionen, XP, drei Leben, Combo-Bonus, Sternen, Rängen, Abzeichen, Blitzrunde und Fehlertraining. Vorlage: `_quellen/werkzeug/trainer.html`. Fragen und Antworten mischt die App bei jedem Durchgang selbst.

```json
{
  "key": "bns-geschichte-trainer", "label": "…", "eyebrow": "…", "description": "…",
  "ranks": [{"xp": 0, "name": "Neuling"}, {"xp": 200, "name": "Spurensucher"}],
  "missions": [
    {"id": "kriegsende", "icon": "🏚️", "title": "…", "subtitle": "…",
     "briefing": ["Lernkarte mit **fett**", "…"],
     "questions": [{"q": "Frage?", "a": "richtige Antwort", "w": ["falsch", "falsch", "falsch"], "info": "Erklärung nach dem Antworten"}]}
  ]
}
```

Missionen werden der Reihe nach freigeschaltet. Fortschritt speichert die App nach Missions-`id` und Fragenposition; deshalb `id` nie ändern und neue Fragen nur ans Ende einer Mission anhängen.

### Aufgabenformen

**Auswahl (2 bis 8 Optionen):**

```json
{
  "num": 1,
  "stem": ["Einleitender Text, ein Absatz je Eintrag."],
  "question": "Die eigentliche Frage?",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": 2,
  "answer_label": "C (Option C)",
  "solution": ["Lösungsweg, ein Absatz je Eintrag.", "Warum die naheliegende falsche Option falsch ist."]
}
```

`answer` zählt ab 0 (0 = A, 1 = B, …).

**Aussagenpaar I/II:** wie Auswahl, zusätzlich `"statements": ["Aussage I", "Aussage II"]`, Optionen genau in dieser Form:

```json
"options": ["Nur Aussage I lässt sich ableiten.", "Nur Aussage II lässt sich ableiten.", "Beide Aussagen lassen sich ableiten.", "Keine der beiden Aussagen lässt sich ableiten."],
"answer_label": "A (Nur I)",
"solution": ["**I ist ableitbar.** Begründung.", "**II ist nicht ableitbar.** Begründung."]
```

Ein gemeinsamer Text für mehrere Aufgaben steht in `"passage": {"label": "Text 1 · Aufgaben 1 und 2", "title": "Titel", "paras": ["Absatz", "Absatz"]}` und wird bei jeder dieser Aufgaben wiederholt.

**Zahleneingabe:**

```json
{"num": 3, "stem": [], "question": "Berechnen Sie $\\frac{3}{4} − \\frac{1}{2}$.", "open": true, "val": 0.25, "answer": null,
 "answer_label": "$\\frac{1}{4}$ (= 0,25)", "solution": ["…"]}
```

Gewertet wird `val` exakt; Brüche wie 1/4 und Dezimalzahlen mit Komma werden akzeptiert, gerundete Dezimalzahlen ab drei Nachkommastellen.

**Bilder:** `"img": "img/a01.png"` zeigt ein Bild über der Frage, `"solimg"` ein Bild in der Lösung. Für Antworten als Bild: `"img2": "img/a01_opt.png", "nopts": 4` statt `options`; das Bild zeigt die Optionen mit den Buchstaben A, B, C, … Pfade gelten relativ zum App-Ordner. PNG oder JPG, höchstens 1 500 Pixel breit.

**Textauszeichnung:** `**fett**` in allen Texten. Formeln in `$…$` mit `\frac{a}{b}`, `\sqrt{x}`, `\sqrt[n]{x}`, `x^{2}`, `x_{1}`, `{log}_{2}`, `\max`, `\min`. Minuszeichen als `−` (U+2212), Malzeichen als `·` oder `×`. Im JSON muss jeder Backslash verdoppelt werden.

## Anforderungen an die Aufgaben

- **Jede Lösung nachrechnen**, am besten mit einem kurzen Python-Skript (Brüche mit `fractions`, Algebra mit `sympy`), bevor sie in die `data.json` geht. Bei Aussagenpaaren jede Rechenaussage einzeln prüfen.
- **Falsche Optionen aus typischen Denkfehlern bilden** (Prozente addiert, Zwischenergebnis, falsche Bezugsgröße, Vorzeichen) und in der Lösung benennen, welcher Fehler zu welcher Option führt.
- **Antwortbuchstaben gleichmäßig verteilen:** In einem Test mit 15 Auswahlaufgaben kommt jeder der vier Buchstaben mindestens dreimal vor.
- **Niveau angeben** (`level`) und innerhalb einer App steigern.
- **Sprache:** Deutsch, sachlich und klar, Ansprache im Du. Keine Gedankenstriche als Stilmittel, keine Floskeln, Zahlen mit Leerzeichen als Tausendertrenner (12 000) und Dezimalkomma.
- Was sich aus den Quellen nicht sicher belegen lässt, nicht als Tatsache in eine Aufgabe schreiben.

## Prüfung vor dem Push

1. `build.py --check` läuft ohne Fehler.
2. Wenn Playwright verfügbar ist: die gebaute App im Browser öffnen, den neuen Test mit den hinterlegten richtigen Antworten durchspielen und prüfen, dass die volle Punktzahl erscheint und keine Skriptfehler auftreten. Das Skript dazu lässt sich in wenigen Zeilen schreiben: Test starten, je Aufgabe `#q .opt[data-k="<answer>"]` antippen oder `#free` mit `val` füllen, `#next`, am Ende `#yes`, dann `.score .big` lesen.
3. `git status` prüfen: Geändert sein dürfen nur die Quellen und die gebauten Dateien des eigenen Projekts.

## Rückmeldung an den Nutzer

Kurz und konkret: welche App, welcher Test, wie viele Aufgaben, auf welchem Niveau, die Adresse der Projektseite und der Hinweis, dass Pages ein bis zwei Minuten braucht. Wenn etwas nicht geprüft werden konnte, das ausdrücklich sagen.
