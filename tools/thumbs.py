# Downloads 400px thumbnails of the Commons files listed in a file into a folder, then draws a labeled contact sheet.
# usage: python3 thumbs.py list.txt outdir
import json, sys, time, urllib.parse, urllib.request, os
from PIL import Image, ImageDraw
UA = {"User-Agent": "adventskalender-kinder/1.0 (private non-commercial advent calendar)"}
def get(url, raw=False):
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read() if raw else json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(10 * (i + 1))
files = [l.strip() for l in open(sys.argv[1]) if l.strip()]
out = sys.argv[2]; os.makedirs(out, exist_ok=True)
urls = {}
for i in range(0, len(files), 40):
    chunk = files[i:i+40]
    q = urllib.parse.urlencode({"action":"query","format":"json","prop":"imageinfo","titles":"|".join("File:"+f for f in chunk),"iiprop":"url","iiurlwidth":330})
    d = get("https://commons.wikimedia.org/w/api.php?"+q)["query"]
    norm = {n["to"]: n["from"] for n in d.get("normalized", [])}
    for p in d["pages"].values():
        key = norm.get(p["title"], p["title"])[5:]
        if "imageinfo" in p: urls[key] = p["imageinfo"][0]["thumburl"]
        else: print("MISSING", key)
for idx, f in enumerate(files):
    if f not in urls: continue
    path = os.path.join(out, f"{idx:02d}.jpg")
    if not os.path.exists(path):
        open(path, "wb").write(get(urls[f], raw=True)); time.sleep(2)
# contact sheets, 4x3 per sheet
cells = [(i, f) for i, f in enumerate(files) if os.path.exists(os.path.join(out, f"{i:02d}.jpg"))]
for s in range(0, len(cells), 12):
    sheet = Image.new("RGB", (4*300, 3*280), "white"); d = ImageDraw.Draw(sheet)
    for k, (i, f) in enumerate(cells[s:s+12]):
        im = Image.open(os.path.join(out, f"{i:02d}.jpg")).convert("RGB"); im.thumbnail((290, 245))
        x, y = (k % 4) * 300, (k // 4) * 280
        sheet.paste(im, (x + 5, y + 5)); d.text((x + 5, y + 255), f"{i:02d} {f[:44]}", fill="black")
    sheet.save(os.path.join(out, f"sheet{s//12}.png"))
print("ok", len(cells))
