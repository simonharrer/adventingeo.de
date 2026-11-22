# Searches Wikimedia Commons files and prints license and size. usage: python3 search.py "query" [n]
import json, sys, time, urllib.parse, urllib.request
UA = {"User-Agent": "adventskalender-kinder/1.0 (private non-commercial advent calendar)"}
def get(url):
    for i in range(6):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r: return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code != 429: raise
            time.sleep(5 * (i + 1))
for query in sys.argv[1:]:
    q = urllib.parse.urlencode({"action":"query","format":"json","generator":"search","gsrsearch":query+" filetype:bitmap","gsrnamespace":6,
        "gsrlimit":8,"prop":"imageinfo","iiprop":"extmetadata|size","iiextmetadatafilter":"LicenseShortName"})
    d = get("https://commons.wikimedia.org/w/api.php?"+q).get("query", {}).get("pages", {})
    print("##", query)
    for p in sorted(d.values(), key=lambda p: p["index"]):
        ii = p["imageinfo"][0]
        print("  ", p["title"][5:], "|", ii["extmetadata"].get("LicenseShortName",{}).get("value"), ii["width"], "x", ii["height"])
    time.sleep(1)
