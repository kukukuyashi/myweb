from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_optional_user
from app.core.db import get_db
from app.core.response import ok
from app.models.anime_watchlist import AnimeWatchlist
from app.models.user import User
from app.services.bangumi_client import (
    BangumiFetchError,
    build_schedule,
    calendar_meta,
    fetch_calendar,
    flatten_season_items,
    items_for_weekday,
    normalize_calendar_item,
    today_weekday_id,
)

router = APIRouter(prefix="/anime", tags=["anime"])


class WatchlistAdd(BaseModel):
    bangumi_id: int
    name: str = Field(min_length=1, max_length=300)
    name_cn: str | None = Field(default=None, max_length=300)
    cover_url: str | None = Field(default=None, max_length=512)
    air_weekday: int | None = Field(default=None, ge=1, le=7)
    air_time: str | None = Field(default=None, max_length=32)


def _watchlist_item(row: AnimeWatchlist) -> dict:
    return {
        "bangumi_id": row.bangumi_id,
        "name": row.name,
        "name_cn": row.name_cn,
        "cover_url": row.cover_url,
        "air_weekday": row.air_weekday,
        "air_time": row.air_time,
        "sort_order": row.sort_order,
    }


@router.get("/schedule", summary="追番表（日历+今日，单次请求）")
async def get_schedule(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
):
    try:
        data = await build_schedule()
    except BangumiFetchError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    my_updates: list[dict] = []
    if current_user:
        watch_ids = {
            r.bangumi_id
            for r in db.query(AnimeWatchlist).filter(AnimeWatchlist.user_id == current_user.id).all()
        }
        my_updates = [i for i in data["today_items"] if i["bangumi_id"] in watch_ids]
    return ok({**data, "my_updates": my_updates})


@router.get("/calendar", summary="Bangumi 放送日历")
async def get_calendar():
    try:
        calendar, source_meta = await fetch_calendar()
    except BangumiFetchError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    meta = calendar_meta(calendar, source_meta)
    season = flatten_season_items(calendar)
    weekdays = [
        {
            "weekday": day.get("weekday"),
            "items": [
                normalize_calendar_item(i, (day.get("weekday") or {}).get("id") or 0)
                for i in day.get("items") or []
            ],
        }
        for day in calendar
    ]
    return ok({"meta": meta, "weekdays": weekdays, "season": season})


@router.get("/today", summary="今日更新")
async def get_today(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User | None, Depends(get_optional_user)] = None,
):
    try:
        calendar, source_meta = await fetch_calendar()
    except BangumiFetchError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    meta = calendar_meta(calendar, source_meta)
    today_id = today_weekday_id()
    today_items = items_for_weekday(calendar, today_id)
    my_updates: list[dict] = []
    if current_user:
        watch_ids = {
            r.bangumi_id
            for r in db.query(AnimeWatchlist).filter(AnimeWatchlist.user_id == current_user.id).all()
        }
        my_updates = [i for i in today_items if i["bangumi_id"] in watch_ids]
    return ok({
        "meta": meta,
        "today_items": today_items,
        "my_updates": my_updates,
    })


@router.get("/watchlist", summary="我的追番")
def get_watchlist(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    rows = (
        db.query(AnimeWatchlist)
        .filter(AnimeWatchlist.user_id == current_user.id)
        .order_by(AnimeWatchlist.sort_order, AnimeWatchlist.id)
        .all()
    )
    return ok({"items": [_watchlist_item(r) for r in rows]})


@router.post("/watchlist", summary="添加追番")
def add_watchlist(
    payload: WatchlistAdd,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    exists = (
        db.query(AnimeWatchlist)
        .filter(
            AnimeWatchlist.user_id == current_user.id,
            AnimeWatchlist.bangumi_id == payload.bangumi_id,
        )
        .first()
    )
    if exists:
        return ok(_watchlist_item(exists), message="已在追番列表")
    row = AnimeWatchlist(
        user_id=current_user.id,
        bangumi_id=payload.bangumi_id,
        name=payload.name,
        name_cn=payload.name_cn,
        cover_url=payload.cover_url,
        air_weekday=payload.air_weekday,
        air_time=payload.air_time,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(_watchlist_item(row), message="已加入追番")


@router.delete("/watchlist/{bangumi_id}", summary="取消追番")
def remove_watchlist(
    bangumi_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_db)],
):
    row = (
        db.query(AnimeWatchlist)
        .filter(
            AnimeWatchlist.user_id == current_user.id,
            AnimeWatchlist.bangumi_id == bangumi_id,
        )
        .first()
    )
    if not row:
        raise HTTPException(status_code=404, detail="未在追番列表")
    db.delete(row)
    db.commit()
    return ok(message="已取消追番")
