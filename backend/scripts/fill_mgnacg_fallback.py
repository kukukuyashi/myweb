"""Batch resolve mgnacg_vod_id for fallback season items."""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.mgnacg_client import _suggest, _search_query, _score_match, play_url
import httpx

DATA = Path(__file__).resolve().parents[1] / "app" / "data" / "bangumi_season_fallback_202607.json"


async def resolve_one(client, item):
    query = _search_query(item.get("name_cn"), item.get("name"))
    candidates = await _suggest(client, query)
    best_id = None
    best_score = 0.0
    for row in candidates:
        score = _score_match(query, row.get("name") or "")
        if score > best_score:
            best_score = score
            best_id = row.get("id")
    if best_id and best_score >= 0.45:
        return best_id, best_score, play_url(best_id)
    return None, best_score, None


async def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    async with httpx.AsyncClient(timeout=8, follow_redirects=True) as client:
        for item in data["items"]:
            if item.get("mgnacg_vod_id"):
                continue
            vid, score, url = await resolve_one(client, item)
            if vid:
                item["mgnacg_vod_id"] = vid
                print(f"OK {item['name_cn']} -> {vid} ({score:.2f})")
            else:
                print(f"SKIP {item['name_cn']} ({score:.2f})")
            await asyncio.sleep(0.15)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    asyncio.run(main())
