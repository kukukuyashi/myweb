import http.cookiejar
import json
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
BASE = "https://www.mgnacg.com"

cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))


def fetch(url, headers=None):
    h = {
        "User-Agent": UA,
        "Accept": "text/html,application/xhtml+xml,application/json,*/*",
        "Accept-Language": "zh-CN,zh;q=0.9",
    }
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with opener.open(req, timeout=15) as r:
        body = r.read().decode("utf-8", "ignore")
        return body, r.geturl(), r.status


# warm cookies
home, home_url, _ = fetch(BASE + "/")
print("home len", len(home), "url", home_url)
print("cookies", [c.name for c in cj])
print("title", re.search(r"<title>([^<]+)</title>", home, re.I))
print("first 500:", home[:500].replace("\n", " "))

# look for any 1604 or vodplay in home
for pat in ["vodplay", "voddetail", "mac_url", "maccms", "path_detail", "path_play", "1604", "1609"]:
    print(pat, home.count(pat))

# extract all hrefs
links = set(re.findall(r'href=["\']([^"\']+)["\']', home))
print("link count", len(links))
for l in sorted(links)[:40]:
    print(" ", l)

vid = 1604
en = "wuzhizhuanshengdisanjidaoliaoyishijiejiunachuzhenbenshi"
paths = [
    f"/vodplay/{vid}-1-1.html",
    f"/vod/{en}.html",
    f"/index.php/vod/play/id/{vid}/sid/1/nid/1.html",
    f"/index.php/vod/detail/id/{vid}.html",
    f"/index.php/vod/play/id/{vid}.html",
    f"/index.php?m=vod-play-id-{vid}-sid-1-nid-1",
    f"/index.php?m=vod-detail-id-{vid}",
]
print("\n=== with cookies ===")
for p in paths:
    try:
        body, final, status = fetch(BASE + p, {"Referer": BASE + "/"})
        title = re.search(r"<title>([^<]+)</title>", body, re.I)
        print("OK", p, status, title.group(1)[:60] if title else body[:100])
    except Exception as e:
        print("FAIL", p, e)

# try ajax vod detail endpoints from maccms
print("\n=== ajax endpoints ===")
for u in [
    f"{BASE}/index.php/ajax/vod?id={vid}",
    f"{BASE}/index.php/ajax/vod?ids={vid}",
    f"{BASE}/index.php/ajax/vod_detail?id={vid}",
    f"{BASE}/index.php/ajax/vod?id={vid}&mid=1",
    f"{BASE}/index.php/ajax/vod?ac=detail&ids={vid}",
    f"{BASE}/index.php/ajax/vod?ac=detail&id={vid}",
    f"{BASE}/index.php/ajax/vod?ac=detail&ids={vid}&mid=1",
]:
    try:
        body, _, status = fetch(u, {"X-Requested-With": "XMLHttpRequest", "Referer": BASE + "/"})
        print("ajax OK", u.replace(BASE, ""), status, body[:200])
    except Exception as e:
        print("ajax FAIL", u.replace(BASE, ""), e)
