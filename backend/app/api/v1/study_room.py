# -*- coding: utf-8 -*-
"""自习室实时聊天:WebSocket + 历史/在线 HTTP"""
from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict
from datetime import timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.db import SessionLocal, get_db
from app.core.response import ok
from app.core.security import ALGORITHM
from app.models.study_room import StudyRoomMessage
from app.models.user import User
from app.schemas.study_room import (
    StudyRoomMessageCreate,
    StudyRoomMessagePublic,
    StudyRoomOnlineResponse,
    StudyRoomOnlineUser,
)
from app.services.cache import _get_client, cache_incr

router = APIRouter(prefix="/study-room", tags=["study-room"])

CHANNEL = "study:room"
ONLINE_KEY_PREFIX = "study:online:"
ONLINE_TTL = 60
RL_TTL = 65
RL_LIMIT_PER_MIN = 20
HISTORY_LIMIT = 50
ONLINE_RECENT_MAX = 12

# 本机 WS 连接池:user_id -> set[WebSocket]
_local_conns: dict[int, set[WebSocket]] = defaultdict(set)


def _client():
    return _get_client()


def _to_public_dict(msg: StudyRoomMessage, user: User | None) -> dict:
    created = msg.created_at
    if created is not None and created.tzinfo is None:
        created_iso = created.replace(tzinfo=timezone.utc).isoformat()
    elif created is not None:
        created_iso = created.isoformat()
    else:
        created_iso = None
    if user is None:
        # 兜底:只暴露 id
        return {
            "id": msg.id,
            "user_id": msg.user_id,
            "username": "",
            "nickname": None,
            "avatar": None,
            "content": msg.content,
            "message_type": msg.message_type or "text",
            "sticker_url": msg.sticker_url,
            "created_at": created_iso,
        }
    return {
        "id": msg.id,
        "user_id": msg.user_id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
        "content": msg.content,
        "message_type": msg.message_type or "text",
        "sticker_url": msg.sticker_url,
        "created_at": created_iso,
    }


def _publish(channel: str, payload: dict) -> None:
    cli = _client()
    if not cli:
        return
    try:
        cli.publish(channel, json.dumps(payload, ensure_ascii=False, default=str))
    except Exception:
        pass


def _set_online(user_id: int) -> None:
    cli = _client()
    if not cli:
        return
    try:
        cli.setex(f"{ONLINE_KEY_PREFIX}{user_id}", ONLINE_TTL, "1")
    except Exception:
        pass


def _clear_online(user_id: int) -> None:
    cli = _client()
    if not cli:
        return
    try:
        cli.delete(f"{ONLINE_KEY_PREFIX}{user_id}")
    except Exception:
        pass


def _collect_online_user_ids() -> list[int]:
    cli = _client()
    if not cli:
        return list(_local_conns.keys())
    try:
        ids: list[int] = []
        for key in cli.scan_iter(f"{ONLINE_KEY_PREFIX}*"):
            try:
                uid = int(key.split(":")[-1])
                ids.append(uid)
            except Exception:
                continue
        # 合并本机连接(可能 Redis 暂时不可用)
        for uid in _local_conns.keys():
            if uid not in ids:
                ids.append(uid)
        return ids
    except Exception:
        return list(_local_conns.keys())


def _rate_limit_check(user_id: int) -> bool:
    cli = _client()
    if not cli:
        return True  # Redis 不可用时不强制限流
    minute = int(time.time() // 60)
    key = f"study:rl:{user_id}:{minute}"
    n = cache_incr(key, RL_TTL)
    return n is None or n <= RL_LIMIT_PER_MIN


def _user_display_dict(user: User) -> dict:
    return {
        "user_id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "avatar": user.avatar,
    }


def _load_users_map(db: Session, user_ids: set[int]) -> dict[int, User]:
    if not user_ids:
        return {}
    out: dict[int, User] = {}
    for u in db.query(User).filter(User.id.in_(user_ids)).all():
        out[u.id] = u
    return out


@router.get("/messages", summary="自习室历史消息")
def list_messages(
    db: Annotated[Session, Depends(get_db)],
    before: int | None = Query(None, description="取 id < before(分页向上滚加载更多)"),
    limit: int = Query(50, ge=1, le=100),
):
    q = db.query(StudyRoomMessage)
    if before is not None:
        q = q.filter(StudyRoomMessage.id < before)
    rows = q.order_by(StudyRoomMessage.id.desc()).limit(limit).all()
    users_map = _load_users_map(db, {r.user_id for r in rows})
    items = [
        StudyRoomMessagePublic.model_validate(_to_public_dict(r, users_map.get(r.user_id))).model_dump()
        for r in rows
    ]
    return ok({"items": items})


@router.get("/online", summary="在线用户")
def list_online(db: Annotated[Session, Depends(get_db)]):
    ids = _collect_online_user_ids()
    # 去重保序
    seen: set[int] = set()
    uniq: list[int] = []
    for i in ids:
        if i in seen:
            continue
        seen.add(i)
        uniq.append(i)
    recent_ids = uniq[-ONLINE_RECENT_MAX:]
    users: list[dict] = []
    if recent_ids:
        users_map = _load_users_map(db, set(recent_ids))
        order = {uid: idx for idx, uid in enumerate(recent_ids)}
        users = [
            _user_display_dict(users_map[uid])
            for uid in recent_ids
            if uid in users_map
        ]
        users.sort(key=lambda x: order.get(x["user_id"], 0))
    return ok({"count": len(uniq), "recent": users})


def _auth_user_from_token(token: str | None) -> User | None:
    if not token:
        return None
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            return None
    except JWTError:
        return None
    db = SessionLocal()
    try:
        return db.query(User).filter(User.username == username).first()
    finally:
        db.close()


async def _broadcast_local(payload: dict) -> None:
    """向本机所有 WS 广播(JSON 字符串)"""
    data = json.dumps(payload, ensure_ascii=False, default=str)
    dead: list[WebSocket] = []
    for ws_set in list(_local_conns.values()):
        for ws in list(ws_set):
            try:
                await ws.send_text(data)
            except Exception:
                dead.append(ws)
    for ws in dead:
        for s in _local_conns.values():
            s.discard(ws)


async def _send_text(ws: WebSocket, payload: dict) -> bool:
    try:
        await ws.send_text(json.dumps(payload, ensure_ascii=False, default=str))
        return True
    except Exception:
        return False


@router.websocket("/ws")
async def study_room_ws(websocket: WebSocket, token: str | None = None):
    tk = token if token is not None else websocket.query_params.get("token")
    user = _auth_user_from_token(tk)
    if user is None:
        await websocket.close(code=4401)
        return

    await websocket.accept()
    _set_online(user.id)
    _local_conns[user.id].add(websocket)

    # 推最近历史
    try:
        db = SessionLocal()
        try:
            rows = (
                db.query(StudyRoomMessage)
                .order_by(StudyRoomMessage.id.desc())
                .limit(HISTORY_LIMIT)
                .all()
            )
            users_map = _load_users_map(db, {r.user_id for r in rows})
            await _send_text(websocket, {
                "type": "history",
                "items": [_to_public_dict(r, users_map.get(r.user_id)) for r in rows],
            })
        finally:
            db.close()
    except Exception:
        pass

    cli = _client()
    stop_event = asyncio.Event()

    async def _redis_subscriber():
        if not cli:
            return
        try:
            pubsub = cli.pubsub()
            pubsub.subscribe(CHANNEL)
            try:
                while not stop_event.is_set():
                    msg = await asyncio.to_thread(
                        pubsub.get_message,
                        True,
                        1.0,
                    )
                    if not msg or msg.get("type") != "message":
                        continue
                    data = msg.get("data")
                    if isinstance(data, bytes):
                        try:
                            data = data.decode("utf-8", "ignore")
                        except Exception:
                            continue
                    if not data:
                        continue
                    try:
                        await websocket.send_text(data)
                    except Exception:
                        break
            finally:
                try:
                    pubsub.unsubscribe(CHANNEL)
                except Exception:
                    pass
                try:
                    pubsub.close()
                except Exception:
                    pass
        except Exception:
            pass

    sub_task = asyncio.create_task(_redis_subscriber())

    try:
        # 30s 心跳 / 消息接收主循环
        while True:
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
            except asyncio.TimeoutError:
                # 30s 内无消息 → 发 ping
                if not await _send_text(websocket, {"type": "ping"}):
                    break
                continue

            _set_online(user.id)  # 续期在线 TTL

            try:
                data = json.loads(raw)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            t = data.get("type")
            if t == "pong":
                continue
            if t == "msg":
                raw_content = data.get("content")
                raw_sticker = data.get("sticker_url")
                content = raw_content.strip() if isinstance(raw_content, str) else ""
                sticker = raw_sticker.strip() if isinstance(raw_sticker, str) else ""
                if not content and not sticker:
                    continue
                if content and len(content) > 500:
                    await _send_text(websocket, {"type": "err", "reason": "too_long"})
                    continue
                if sticker and len(sticker) > 512:
                    await _send_text(websocket, {"type": "err", "reason": "too_long"})
                    continue
                # sticker URL 白名单:防滥用(仅允许同源静态 + 后端 uploads)
                if sticker:
                    allowed = (
                        sticker.startswith("https://")
                        or sticker.startswith("/myweb/img/bqb/")
                        or sticker.startswith("/uploads/")
                    )
                    if not allowed:
                        await _send_text(websocket, {"type": "err", "reason": "bad_sticker"})
                        continue
                if not _rate_limit_check(user.id):
                    await _send_text(websocket, {"type": "err", "reason": "rate"})
                    continue
                # 落库 + 广播
                try:
                    db = SessionLocal()
                    try:
                        row = StudyRoomMessage(
                            user_id=user.id,
                            content=content or None,
                            message_type="sticker" if sticker else "text",
                            sticker_url=sticker or None,
                        )
                        db.add(row)
                        db.commit()
                        db.refresh(row)
                        payload = {
                            "type": "msg",
                            **_to_public_dict(row, user),
                        }
                    finally:
                        db.close()
                    _publish(CHANNEL, payload)
                except Exception:
                    continue
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        stop_event.set()
        if sub_task and not sub_task.done():
            sub_task.cancel()
            try:
                await sub_task
            except Exception:
                pass
        _local_conns[user.id].discard(websocket)
        if not _local_conns[user.id]:
            del _local_conns[user.id]
        _clear_online(user.id)
        try:
            await _broadcast_local({"type": "presence", "event": "leave", "user_id": user.id})
        except Exception:
            pass