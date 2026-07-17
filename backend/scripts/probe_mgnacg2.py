import json
import re
import urllib.parse
import urllib.request

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
BASE = "https://www.mgnacg.com"


def fetch(url, headers=None):
    h = {"User-Agent": UA, "Accept": "text/html,application/xhtml+xml,application/json"}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", "ignore"), r.geturl(), r.status, dict(r.headers)


def try_url(path, extra_headers=None):
    full = BASE + path if path.startswith("/") else path
    try:
        body, final, status, _ = fetch(full, extra_headers)
        title = re.search(r"<title>([^<]+)</title>", body, re.I)
        print("OK", status, path[:80], title.group(1)[:50] if title else body[:80])
        return body
    except Exception as exc:
        print("FAIL", path[:80], str(exc)[:80])
        return None


# homepage config
html, _, _, _ = fetch(BASE + "/")
print("=== maccms vars ===")
for pat in [
    r"var\s+maccms\s*=\s*(\{[^;]+\})",
    r"MAC\.(?:Config|Global)\s*=\s*(\{[^;]+\})",
    r'"path"\s*:\s*"([^"]+)"',
    r"path_detail\s*[:=]\s*['\"]([^'\"]+)['\"]",
    r"path_play\s*[:=]\s*['\"]([^'\"]+)['\"]",
    r"vodlink[^\"']*['\"]([^'\"]+)['\"]",
]:
    for m in re.findall(pat, html):
        print(pat[:30], "->", str(m)[:120])

print("\n=== script src ===")
for m in re.findall(r'src=["\']([^"\']+\.js[^"\']*)["\']', html):
    if "jquery" not in m.lower():
        print(m)

print("\n=== inline vod links ===")
for m in re.findall(r'["\'](/[^"\']*(?:vod|play|detail)[^"\']*)["\']', html):
    print(m)

# try with referer
print("\n=== with referer ===")
for path in [
    "/vodplay/1604-1-1.html",
    "/vod/wuzhizhuanshengdisanjidaoliaoyishijiejiunachuzhenbenshi.html",
    "/index.php/vod/play/id/1604/sid/1/nid/1.html",
]:
    try_url(path, {"Referer": BASE + "/"})

# search mac_wd ajax
print("\n=== search ajax ===")
kw = urllib.parse.quote("无职转生")
for u in [
    f"{BASE}/index.php/ajax/search?mid=1&wd={kw}&page=1&limit=5",
    f"{BASE}/index.php/vod/search.html?wd={kw}",
    f"{BASE}/index.php/vod/search?wd={kw}",
]:
    body = try_url(u.replace(BASE, ""))

# fetch a JS file for path config
print("\n=== app js scan ===")
for js_path in re.findall(r'src=["\']([^"\']+\.js)["\']', html)[:8]:
    if js_path.startswith("//"):
        js_path = "https:" + js_path
    elif js_path.startswith("/"):
        js_path = BASE + js_path
    try:
        js, _, _, _ = fetch(js_path)
        for kw in ("vodplay", "path_play", "path_detail", "vod/detail", "vod/play"):
            if kw in js:
                idx = js.find(kw)
                print(js_path.split("/")[-1], kw, js[max(0, idx - 40): idx + 80].replace("\n", " "))
    except Exception as e:
        print("js fail", js_path, e)
