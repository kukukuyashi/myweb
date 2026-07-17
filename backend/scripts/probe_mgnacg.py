import json
import re
import urllib.parse
import urllib.request

UA = "CYINC/1.0"
BASE = "https://www.mgnacg.com"


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=12) as r:
        return r.read().decode("utf-8", "ignore"), r.geturl(), r.status


def try_url(path_or_url):
    full = path_or_url if path_or_url.startswith("http") else BASE + path_or_url
    try:
        body, final, status = fetch(full)
        title = re.search(r"<title>([^<]+)</title>", body, re.I)
        print("OK", status, path_or_url, "->", final, title.group(1)[:60] if title else "")
        return True
    except Exception as exc:
        print("FAIL", path_or_url, exc)
        return False


vid = 1604
en = "wuzhizhuanshengdisanjidaoliaoyishijiejiunachuzhenbenshi"

patterns = [
    f"/vod/{en}.html",
    f"/vod/{en}/",
    f"/voddetail/{vid}.html",
    f"/vodplay/{vid}-1-1.html",
    f"/vodplay/{en}-1-1.html",
    f"/index.php/vod/detail/id/{vid}.html",
    f"/index.php/vod/play/id/{vid}/sid/1/nid/1.html",
    f"/index.php/vod/play/id/{vid}.html",
    f"/index.php/vod/detail/id/{vid}",
    f"/index.php/vod/play/id/{vid}/sid/1/nid/1",
    f"/vod/{vid}.html",
    f"/detail/{en}.html",
    f"/play/{en}.html",
    f"/play/{vid}-1-1.html",
    f"/anime/{en}.html",
    f"/bangumi/{en}.html",
]
print("=== URL patterns ===")
for pat in patterns:
    try_url(pat)

print("\n=== suggest ===")
kw = urllib.parse.quote("无职转生")
req = urllib.request.Request(
    f"{BASE}/index.php/ajax/suggest?mid=1&wd={kw}&limit=3&timestamp=1",
    headers={"User-Agent": UA},
)
suggest = json.loads(urllib.request.urlopen(req, timeout=12).read())
print(json.dumps(suggest, ensure_ascii=False, indent=2))

print("\n=== homepage links ===")
html, _, _ = fetch(BASE + "/")
for m in re.findall(r'href=["\']([^"\']+)["\']', html):
    if any(k in m for k in ("vod", "play", "detail", "anime")):
        if m not in {"/index.php/vod/show/id/1.html", "/user/plays/"}:
            print("link", m)

print("\n=== ajax data first item ===")
body, _, _ = fetch(f"{BASE}/index.php/ajax/data?mid=1&page=1&limit=3")
data = json.loads(body)
if data.get("list"):
    item = data["list"][0]
    print(json.dumps(item, ensure_ascii=False, indent=2)[:800])
    vod_id = item.get("vod_id")
    vod_en = item.get("vod_en") or item.get("en") or ""
    for pat in [
        f"/vod/{vod_en}.html" if vod_en else None,
        f"/vodplay/{vod_id}-1-1.html",
        f"/voddetail/{vod_id}.html",
        f"/index.php/vod/detail/id/{vod_id}.html",
        f"/index.php/vod/play/id/{vod_id}/sid/1/nid/1.html",
    ]:
        if pat:
            try_url(pat)
