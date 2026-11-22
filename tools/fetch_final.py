# Downloads the chosen images (960px wide, 1280 for the crop source) from Wikimedia Commons into <calendar>/bilder/
# and writes the license evidence (Commons metadata as of the download) to <calendar>/bilder/lizenzen.json.
import json, os, time, re, html, urllib.parse, urllib.request, datetime
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "adventskalender-kinder/1.0 (private non-commercial advent calendar)"}
def get(url, raw=False):
    for i in range(8):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read() if raw else json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(10 * (i + 1))
    raise RuntimeError("rate limited: " + url)
def text(s):  # strip HTML from Commons metadata
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()
cfg = json.load(open(os.path.join(ROOT, "tools", "images.json")))
now = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
for cal, items in cfg.items():
    outdir = os.path.join(ROOT, cal, "bilder"); os.makedirs(outdir, exist_ok=True)
    evidence = {}
    names = list(items)
    for i in range(0, len(names), 25):
        chunk = names[i:i+25]
        q = urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","titles":"|".join("File:"+items[n] for n in chunk),
            "iiprop":"url|extmetadata|size|sha1|timestamp","iiurlwidth":960})
        d = get("https://commons.wikimedia.org/w/api.php?"+q)["query"]
        norm = {x["to"]: x["from"] for x in d.get("normalized", [])}
        byfile = {norm.get(p["title"], p["title"])[5:]: p for p in d["pages"].values()}
        for n in chunk:
            p = byfile[items[n]]; ii = p["imageinfo"][0]; m = ii["extmetadata"]
            g = lambda k: m.get(k, {}).get("value", "")
            evidence[n] = {
                "datei": p["title"],
                "commonsSeite": ii["descriptionurl"],
                "urheber": text(g("Artist")),
                "quelle": text(g("Credit")),
                "lizenz": g("LicenseShortName"),
                "lizenzUrl": g("LicenseUrl"),
                "nutzungsbedingungen": text(g("UsageTerms")),
                "urheberrechtlichGeschuetzt": g("Copyrighted"),
                "namensnennungNoetig": g("AttributionRequired"),
                "beschreibung": text(g("ImageDescription"))[:300],
                "original": {"url": ii["url"], "breite": ii["width"], "hoehe": ii["height"], "sha1": ii["sha1"], "hochgeladen": ii["timestamp"]},
                "abgerufen": now,
            }
            path = os.path.join(outdir, n + ".jpg")
            if not os.path.exists(path):
                url = ii["thumburl"]
                if n == "greif": url = url.replace("/960px-", "/1920px-")
                raw = os.path.join(outdir, n + ".tmp"); open(raw, "wb").write(get(url, raw=True)); time.sleep(2)
                im = Image.open(raw).convert("RGB")
                if n == "greif":  # griffin, top left of the Bertuch plate
                    w, h = im.size; im = im.crop((int(w * 0.0), int(h * 0.0), int(w * 0.55), int(h * 0.335)))
                    evidence[n]["bearbeitung"] = "Ausschnitt (der Greif oben links auf der Tafel)"
                im.thumbnail((960, 960)); im.save(path, "JPEG", quality=82, optimize=True); os.remove(raw)
            print(cal, n, evidence[n]["lizenz"], "|", evidence[n]["urheber"][:60])
    json.dump(evidence, open(os.path.join(outdir, "lizenzen.json"), "w"), ensure_ascii=False, indent=1)
