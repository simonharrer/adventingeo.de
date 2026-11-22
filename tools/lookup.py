# Looks up the lead images of Wikipedia articles (batched) and their licenses on Wikimedia Commons.
# usage: python3 lookup.py de|en "Artikel1" "Artikel2" ...
import json, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "adventskalender-kinder/1.0 (private non-commercial advent calendar)"}
def get(url):
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(5 * (i + 1))
    raise RuntimeError("rate limited")
def leads(lang, titles):
    q = urllib.parse.urlencode({"action":"query","format":"json","prop":"pageimages","piprop":"name","titles":"|".join(titles),"redirects":1})
    d = get(f"https://{lang}.wikipedia.org/w/api.php?{q}")["query"]
    back = {t: t for t in titles}
    for k in ("normalized", "redirects"):
        for x in d.get(k, []):
            for t, v in list(back.items()):
                if v == x["from"]: back[t] = x["to"]
    by = {p["title"]: p.get("pageimage") for p in d["pages"].values()}
    return {t: by.get(back[t]) for t in titles}
def infos(files):
    q = urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","titles":"|".join("File:"+f for f in files),
        "iiprop":"extmetadata|size","iiextmetadatafilter":"LicenseShortName"})
    d = get("https://commons.wikimedia.org/w/api.php?"+q)["query"]
    out = {}
    for p in d["pages"].values():
        ii = p.get("imageinfo")
        out[p["title"][5:].replace(" ", "_")] = (ii[0]["extmetadata"].get("LicenseShortName",{}).get("value"), ii[0]["width"], ii[0]["height"]) if ii else "NOT ON COMMONS"
    return out
lang, titles = sys.argv[1], sys.argv[2:]
l = leads(lang, titles)
inf = infos([f for f in l.values() if f])
for t in titles:
    f = l[t]; print(f"{t} | {f} | {inf.get(f.replace(' ','_')) if f else '-'}")
