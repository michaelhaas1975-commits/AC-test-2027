#!/usr/bin/env python3
"""Baut die Lern-Apps aus den Quelldaten.

Aufruf aus dem Wurzelverzeichnis des Repositorys:
    python3 _quellen/werkzeug/build.py            # alle Projekte
    python3 _quellen/werkzeug/build.py ac         # nur ein Projekt
    python3 _quellen/werkzeug/build.py --check    # nur prüfen, nichts schreiben

Struktur:
    _quellen/werkzeug/template.html        App-Vorlage (für alle Projekte gleich)
    _quellen/<projekt>/projekt.json        Titel, Zielordner und Liste der Apps
    _quellen/<projekt>/<app>/data.json     Tests und Aufgaben einer App
    _quellen/<projekt>/<app>/img/...       Bilder, auf die data.json verweist (optional)
    _quellen/<projekt>/<fach>/<app>/...    dasselbe bei Projekten mit Fächerebene ('faecher')
    _quellen/werkzeug/trainer.html         Vorlage für Apps mit "typ": "trainer" (Lerntrainer)

Das Format von projekt.json und data.json beschreibt ANLEITUNG.md.
"""
import base64, html, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SRC = os.path.join(ROOT, "_quellen")
TEMPLATE = os.path.join(SRC, "werkzeug", "template.html")
TRAINER = os.path.join(SRC, "werkzeug", "trainer.html")
LETTERS = "ABCDEFGH"


class Fehler(Exception):
    pass


def check_item(where, it, n_expected):
    if it.get("num") != n_expected:
        raise Fehler(f"{where}: 'num' muss {n_expected} sein, ist {it.get('num')!r}")
    if not (it.get("question") or it.get("statements") or it.get("img")):
        raise Fehler(f"{where}: braucht 'question', 'statements' oder 'img'")
    if it.get("open"):
        if not isinstance(it.get("val"), (int, float)):
            raise Fehler(f"{where}: offene Aufgabe braucht eine Zahl in 'val'")
    elif it.get("options"):
        k = len(it["options"])
        if not 2 <= k <= 8:
            raise Fehler(f"{where}: 2 bis 8 Optionen erlaubt, sind {k}")
        if not isinstance(it.get("answer"), int) or not 0 <= it["answer"] < k:
            raise Fehler(f"{where}: 'answer' muss ein Index von 0 bis {k - 1} sein")
    elif it.get("nopts"):
        if not it.get("img2"):
            raise Fehler(f"{where}: Bildoptionen ('nopts') brauchen 'img2'")
        if not isinstance(it.get("answer"), int) or not 0 <= it["answer"] < it["nopts"]:
            raise Fehler(f"{where}: 'answer' außerhalb der Bildoptionen")
    else:
        raise Fehler(f"{where}: braucht 'options', 'nopts' oder 'open'")
    if it.get("statements") is not None and len(it["statements"]) != 2:
        raise Fehler(f"{where}: 'statements' muss genau zwei Aussagen enthalten")
    if not it.get("answer_label"):
        raise Fehler(f"{where}: 'answer_label' fehlt")
    if not isinstance(it.get("solution"), list) or not it["solution"]:
        raise Fehler(f"{where}: 'solution' muss eine nichtleere Liste von Absätzen sein")
    for t in [it.get("question") or ""] + list(it.get("stem") or []) + list(it.get("options") or []) + list(it.get("solution") or []):
        if t.count("$") % 2:
            raise Fehler(f"{where}: ungerade Zahl von $-Zeichen (Formel nicht geschlossen): {t[:60]}")


def check_data(where, d):
    for k in ("key", "label", "tests"):
        if k not in d:
            raise Fehler(f"{where}: Feld '{k}' fehlt")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", d["key"]):
        raise Fehler(f"{where}: 'key' nur aus Kleinbuchstaben, Ziffern und Bindestrich")
    if not d["tests"]:
        raise Fehler(f"{where}: keine Tests")
    for ti, t in enumerate(d["tests"]):
        for k in ("name", "level", "minutes", "items"):
            if k not in t:
                raise Fehler(f"{where}, Test {ti + 1}: Feld '{k}' fehlt")
        if not isinstance(t["minutes"], int) or t["minutes"] < 0:
            raise Fehler(f"{where}, Test {ti + 1}: 'minutes' ganze Zahl ≥ 0 (0 = ohne Zeitlimit)")
        if not t["items"]:
            raise Fehler(f"{where}, Test {ti + 1}: keine Aufgaben")
        for i, it in enumerate(t["items"]):
            check_item(f"{where}, Test {ti + 1}, Aufgabe {i + 1}", it, i + 1)


def check_trainer(where, d):
    """Lerntrainer: Missionen mit Fragen; die App mischt die Antworten selbst."""
    for k in ("key", "label", "missions"):
        if k not in d:
            raise Fehler(f"{where}: Feld '{k}' fehlt")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]*", d["key"]):
        raise Fehler(f"{where}: 'key' nur aus Kleinbuchstaben, Ziffern und Bindestrich")
    if not d["missions"]:
        raise Fehler(f"{where}: keine Missionen")
    ids = set()
    for mi, m in enumerate(d["missions"]):
        w = f"{where}, Mission {mi + 1}"
        for k in ("id", "title", "briefing", "questions"):
            if k not in m:
                raise Fehler(f"{w}: Feld '{k}' fehlt")
        if m["id"] in ids:
            raise Fehler(f"{w}: 'id' {m['id']!r} doppelt")
        ids.add(m["id"])
        if not m["questions"]:
            raise Fehler(f"{w}: keine Fragen")
        for qi, q in enumerate(m["questions"]):
            wq = f"{w}, Frage {qi + 1}"
            if not q.get("q") or not q.get("a") or not q.get("info"):
                raise Fehler(f"{wq}: braucht 'q', 'a' (richtige Antwort) und 'info'")
            wrong = q.get("w") or []
            if not 1 <= len(wrong) <= 5:
                raise Fehler(f"{wq}: 'w' braucht 1 bis 5 falsche Antworten")
            if q["a"] in wrong or len(set(wrong)) != len(wrong):
                raise Fehler(f"{wq}: Antworten nicht eindeutig")


def inline_images(d, appdir):
    for t in d["tests"]:
        for it in t["items"]:
            for f in ("img", "img2", "solimg"):
                p = it.get(f)
                if p and not p.startswith("data:"):
                    full = os.path.join(appdir, p)
                    if not os.path.exists(full):
                        raise Fehler(f"Bild fehlt: {full}")
                    ext = os.path.splitext(p)[1].lower().lstrip(".")
                    mime = {"png": "image/png", "jpg": "image/jpeg", "jpeg": "image/jpeg", "svg": "image/svg+xml", "webp": "image/webp"}.get(ext)
                    if not mime:
                        raise Fehler(f"Bildformat nicht unterstützt: {p}")
                    it[f] = f"data:{mime};base64," + base64.b64encode(open(full, "rb").read()).decode()


def page(title, data, template=TEMPLATE):
    tpl = open(template, encoding="utf-8").read()
    body = tpl.replace("__TITLE__", html.escape(title)).replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/"))
    head, rest = body.split("<style>", 1)
    return ('<!doctype html>\n<html lang="de">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            '<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="robots" content="noindex">\n' + head +
            '<style>\nhtml{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}\n' +
            rest.replace("</style>", "</style>\n</head>\n<body>", 1) + "\n</body>\n</html>\n")


INDEX = """<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="robots" content="noindex">
<title>{title}</title>
<style>
:root{{--bg:#f3f5f7;--surface:#fff;--ink:#18232f;--muted:#5b6876;--line:#d6dde4;--accent:#1d4e6b}}
@media (prefers-color-scheme:dark){{:root{{--bg:#10171e;--surface:#18222c;--ink:#e6edf3;--muted:#9aa8b5;--line:#2c3a47;--accent:#7fb6d6}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:17px/1.55 -apple-system,"Helvetica Neue",Arial,sans-serif}}
main{{max-width:760px;margin:0 auto;padding:28px 16px 60px}}
h1{{font-size:2rem;margin:.2em 0 .1em;line-height:1.15}}
.eyebrow{{font-size:.74rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}}
p{{color:var(--muted);margin:.4em 0 1.4em}}
a.card{{display:block;background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:18px 20px;margin-bottom:12px;color:inherit;text-decoration:none;-webkit-tap-highlight-color:transparent}}
a.card strong{{display:block;font-size:1.15rem;color:var(--accent)}}
a.card span{{color:var(--muted);font-size:.95rem}}
small{{color:var(--muted);display:block;margin-top:22px}}
</style>
</head>
<body>
<main>
{back}<span class="eyebrow">{eyebrow}</span>
<h1>{h1}</h1>
<p>{desc}</p>
{cards}
<small>Tipp für das iPad: In Safari auf Teilen tippen und „Zum Home-Bildschirm“ wählen. Dann öffnet sich die Seite wie eine App.</small>
</main>
</body>
</html>
"""


def build_apps(name, pdir, outdir, apps, defaults, write, keys_seen, back=None):
    """Prüft und baut eine Liste von Apps; liefert die Karten für die Übersichtsseite."""
    cards = []
    for a in apps:
        appdir = os.path.join(pdir, a["ordner"])
        d = json.load(open(os.path.join(appdir, "data.json"), encoding="utf-8"))
        where = f"{os.path.relpath(appdir, SRC)}/data.json"
        trainer = a.get("typ") == "trainer"
        (check_trainer if trainer else check_data)(where, d)
        if keys_seen is not None:
            if d["key"] in keys_seen:
                raise Fehler(f"{where}: 'key' {d['key']!r} schon in {keys_seen[d['key']]} vergeben; Ergebnisse würden sich vermischen")
            keys_seen[d["key"]] = where
        for f in ("eyebrow", "description", "rules", "rules_title"):
            if f in defaults and f not in d:
                d[f] = defaults[f]
        if back and "back" not in d:
            d["back"] = back
        if trainer:
            n_q = sum(len(m["questions"]) for m in d["missions"])
            print(f"  {os.path.relpath(os.path.join(outdir, a['datei']), ROOT)}: Lerntrainer, {len(d['missions'])} Missionen, {n_q} Fragen")
            sub = a.get("untertitel") or f"{len(d['missions'])} Missionen"
        else:
            inline_images(d, appdir)
            n_items = sum(len(t["items"]) for t in d["tests"])
            print(f"  {os.path.relpath(os.path.join(outdir, a['datei']), ROOT)}: {len(d['tests'])} Tests, {n_items} Aufgaben")
            sub = a.get("untertitel") or f"{len(d['tests'])} Übungstests"
        if write:
            os.makedirs(outdir, exist_ok=True)
            open(os.path.join(outdir, a["datei"]), "w", encoding="utf-8").write(
                page(a.get("app_titel", d["label"]), d, TRAINER if trainer else TEMPLATE))
        cards.append(f'<a class="card" href="{html.escape(a["datei"])}"><strong>{html.escape(a.get("karte", d["label"]))}</strong><span>{html.escape(sub)}</span></a>')
    return cards


def write_index(path, title, eyebrow, h1, desc, cards, back=None):
    back_html = f'<a href="{html.escape(back["href"])}" style="display:inline-block;margin-bottom:14px;color:var(--accent);font-weight:700;text-decoration:none">← {html.escape(back["label"])}</a><br>' if back else ""
    open(path, "w", encoding="utf-8").write(INDEX.format(
        title=html.escape(title), eyebrow=html.escape(eyebrow), h1=html.escape(h1),
        desc=html.escape(desc), cards="\n".join(cards), back=back_html))


def build_project(name, write=True, keys_seen=None):
    """Ein Projekt hat entweder eine flache Liste 'apps' oder eine Fächerebene 'faecher'
    (Startseite mit Fachwahl, je Fach eine Übersicht mit dessen Apps)."""
    pdir = os.path.join(SRC, name)
    P = json.load(open(os.path.join(pdir, "projekt.json"), encoding="utf-8"))
    for k in ("titel", "ziel"):
        if k not in P:
            raise Fehler(f"{name}/projekt.json: Feld '{k}' fehlt")
    if "apps" not in P and "faecher" not in P:
        raise Fehler(f"{name}/projekt.json: braucht 'apps' oder 'faecher'")
    outdir = os.path.join(ROOT, P["ziel"])
    defaults = P.get("app_defaults", {})
    cards = build_apps(name, pdir, outdir, P.get("apps", []), defaults, write, keys_seen)
    for f in P.get("faecher", []):
        for k in ("ordner", "titel", "apps"):
            if k not in f:
                raise Fehler(f"{name}/projekt.json, Fach {f.get('titel', '?')}: Feld '{k}' fehlt")
        fdir = os.path.join(outdir, f["ordner"])
        fdefaults = dict(defaults, **f.get("app_defaults", {}))
        fcards = build_apps(name, os.path.join(pdir, f["ordner"]), fdir, f["apps"], fdefaults, write, keys_seen,
                            back={"href": "index.html", "label": f"Übersicht {f['titel']}"})
        if write:
            write_index(os.path.join(fdir, "index.html"), f"{f['titel']} · {P['titel']}", f.get("eyebrow", P.get("eyebrow", "")),
                        f["titel"], f.get("beschreibung", ""), fcards, back={"href": "../index.html", "label": "Fächerauswahl"})
        cards.append(f'<a class="card" href="{html.escape(f["ordner"])}/"><strong>{html.escape(f["titel"])}</strong><span>{html.escape(f.get("untertitel", ""))}</span></a>')
    if write:
        write_index(os.path.join(outdir, "index.html"), P["titel"], P.get("eyebrow", ""), P.get("ueberschrift", P["titel"]),
                    P.get("beschreibung", ""), cards)
    return P["ziel"]


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    write = "--check" not in sys.argv
    projects = sorted(p for p in os.listdir(SRC) if os.path.isfile(os.path.join(SRC, p, "projekt.json")))
    keys = {}
    targets = {}
    try:
        for p in projects:                                  # alle prüfen, damit Schlüssel und Ziele eindeutig bleiben
            print(f"Projekt {p}")
            z = build_project(p, write=write and (not args or p in args), keys_seen=keys)
            if z in targets:
                raise Fehler(f"Zielordner {z!r} von {targets[z]} und {p} doppelt belegt")
            targets[z] = p
    except Fehler as e:
        print("FEHLER:", e)
        sys.exit(1)
    print("fertig" if write else "Prüfung bestanden")


if __name__ == "__main__":
    main()
