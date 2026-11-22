# Erzeugt aus bilder/lizenzen.json (Lizenzdaten von Wikimedia Commons, siehe fetch_final.py):
#   <kalender>/bilder/nachweise.js   Bildnachweise für die Seite
#   <kalender>/bilder/klein/*.jpg    kleine Vorschaubilder für die geöffneten Türchen
#   BILDNACHWEISE.md                 Übersicht aller Bilder mit Lizenz und Quelle
import json, os
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Lesbare Urheberangaben, wo die Commons-Metadaten leer oder unübersichtlich sind (Werte von der Commons-Seite).
URHEBER = {
    "anglerfisch": "August Brauer: Die Tiefsee-Fische (Valdivia-Expedition), 1906",
    "blauwal": "NOAA Fisheries",
    "riesenkrake": "NOAA / R. N. Lea",
    "seeschlange": "Olaus Magnus: Historia de Gentibus Septentrionalibus, 1555",
    "phoenix": "Aberdeen-Bestiarium, um 1200",
    "einhorn": "Einhorn-Teppiche, Südniederlande, um 1500 (The Metropolitan Museum of Art)",
    "netzpython": "Mariluna",
    "qilin": "Shen Du zugeschrieben, um 1414 (Philadelphia Museum of Art)",
    "wanderfalke": "Georges Lignier",
    "roch": "aus „The Story of Marco Polo“, 1899 (Internet Archive Book Images)",
    "wolpertinger": "Rainer Zenz (nach Albrecht Dürers „Feldhase“)",
    "kitsune": "Utagawa Hiroshige, 1857 (The Metropolitan Museum of Art)",
    "greif": "Friedrich Justin Bertuch: Bilderbuch für Kinder, um 1800",
    "meerjungfrau": "Charles Robinson (Illustration zu Andersens Märchen)",
    "pegasus": "Rosa Bonheur",
    "drache": "Warwick Goble",
    "riesenkalmar": "Addison Emery Verrill (um 1880)",
    "lederschildkroete": "U.S. Fish and Wildlife Service",
    "groenlandhai": "NOAA Okeanos Explorer Program",
    "mondfisch": "NOAA",
    "barriereriff": "NASA (MISR)",
    "orca": "Robert Pittman (NOAA)",
    "delfin": "NASA",
    "seekuh": "Keith Ramos, U.S. Fish and Wildlife Service",
    "giraffe": "John Walker",
    "narwal": "Kristin Laidre, Polar Science Center, UW / NOAA",
    "skarabaeus": "Claude Valette",
    "seeotter": "Mike Baird",
    "kaiserpinguin": "Ian Duffy",
    "albatros": "JJ Harrison",
    "faecherfisch": "Citron",
}
LIZENZ = {"Public domain": "Gemeinfrei (Public Domain)", "CC0": "CC0 (gemeinfrei)",
          "No restrictions": "Keine bekannten Urheberrechtsbeschränkungen (Flickr Commons)"}

md = ["# Bildnachweise", "",
      "Alle Bilder stammen von Wikimedia Commons. Für jedes Bild sind hier Urheber, Lizenz und die Commons-Seite angegeben,",
      "auf der die Lizenz dokumentiert ist. Die vollständigen Lizenzdaten zum Zeitpunkt des Abrufs (Commons-API, inkl. SHA1 der",
      "Originaldatei) liegen in `<kalender>/bilder/lizenzen.json`.", "",
      "Erlaubt sind nur freie Lizenzen: gemeinfrei (Public Domain, PD-Art, PD-old, Werke von US-Bundesbehörden wie NOAA/NASA),",
      "CC0, CC BY und CC BY-SA. Die CC-Bilder werden mit Namensnennung und Lizenzlink direkt unter dem Bild gezeigt.", ""]
for cal in ("meereszauber", "zauber-der-tiere"):
    base = os.path.join(ROOT, cal, "bilder")
    ev = json.load(open(os.path.join(base, "lizenzen.json")))
    os.makedirs(os.path.join(base, "klein"), exist_ok=True)
    out = {}
    for key, e in ev.items():
        lizenz = LIZENZ.get(e["lizenz"], e["lizenz"])
        out[key] = {
            "datei": e["datei"].replace("File:", "Datei:"),
            "urheber": URHEBER.get(key) or e["urheber"] or "unbekannt",
            "lizenz": lizenz,
            "lizenzUrl": e["lizenzUrl"] or e["commonsSeite"],
            "quelle": e["commonsSeite"],
            "bearbeitung": e.get("bearbeitung", ""),
        }
        klein = os.path.join(base, "klein", key + ".jpg")
        im = Image.open(os.path.join(base, key + ".jpg"))
        im.thumbnail((360, 360)); im.save(klein, "JPEG", quality=78, optimize=True)
    with open(os.path.join(base, "nachweise.js"), "w") as f:
        f.write("// Erzeugt von tools/build.py aus lizenzen.json. Nicht von Hand ändern.\n")
        f.write("window.NACHWEISE = " + json.dumps(out, ensure_ascii=False, indent=1) + ";\n")
    inhalt = open(os.path.join(ROOT, cal, "inhalt.js")).read()
    md += [f"## {cal}", "", "| Motiv | Datei auf Commons | Urheber | Lizenz |", "|---|---|---|---|"]
    for key, e in sorted(out.items(), key=lambda kv: inhalt.find(f'bild: "{kv[0]}"')):
        lz = f"[{e['lizenz']}]({e['lizenzUrl']})" if e["lizenzUrl"] != e["quelle"] else e["lizenz"]
        name = e["datei"].replace("|", "\\|")
        md.append(f"| {key} | [{name}]({e['quelle']}) | {e['urheber'].replace('|', '/')}{' – ' + e['bearbeitung'] if e['bearbeitung'] else ''} | {lz} |")
    md.append("")
open(os.path.join(ROOT, "BILDNACHWEISE.md"), "w").write("\n".join(md))
print("ok")
