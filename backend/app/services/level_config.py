"""账号等级与经验值配置"""

from dataclasses import dataclass


@dataclass(frozen=True)
class LevelTier:
    level: int
    title: str
    xp_required: int
    perks: tuple[str, ...]


@dataclass(frozen=True)
class XpAction:
    xp: int
    daily_max: int
    label: str


LEVEL_TIERS: tuple[LevelTier, ...] = (
    LevelTier(1, "一阶", 0, ()),
    LevelTier(2, "二阶", 500, ("论坛昵称旁显示 Lv.2 徽章",)),
    LevelTier(3, "三阶", 1500, ("头像橙色描边",)),
    LevelTier(4, "四阶", 4000, ("发帖带「四阶」标记",)),
    LevelTier(5, "五阶", 10000, ("头像动态光环框",)),
)

XP_ACTIONS: dict[str, XpAction] = {
    "thread_create": XpAction(30, 3, "发帖"),
    "reply_create": XpAction(12, 20, "评论回复"),
    "thread_like_given": XpAction(3, 40, "点赞帖子"),
    "thread_like_received": XpAction(8, 25, "帖子被点赞"),
    "reply_like_given": XpAction(2, 50, "点赞评论"),
    "reply_like_received": XpAction(5, 30, "评论被点赞"),
    "thread_share": XpAction(10, 8, "分享帖子"),
}

BASE_CHECKIN_XP = 15
STREAK_BONUS_CAP = 7
STREAK_BONUS_PER_DAY = 3
STREAK_MILESTONE_DAYS = 7
STREAK_MILESTONE_BONUS = 25


def level_from_xp(xp: int) -> int:
    current = 1
    for tier in LEVEL_TIERS:
        if xp >= tier.xp_required:
            current = tier.level
    return current


def get_tier(level: int) -> LevelTier:
    for tier in reversed(LEVEL_TIERS):
        if tier.level <= level:
            return tier
    return LEVEL_TIERS[0]


def next_tier(level: int) -> LevelTier | None:
    for tier in LEVEL_TIERS:
        if tier.level > level:
            return tier
    return None


def calc_checkin_xp(streak_after: int) -> int:
    bonus = min(streak_after, STREAK_BONUS_CAP) * STREAK_BONUS_PER_DAY
    xp = BASE_CHECKIN_XP + bonus
    if streak_after == STREAK_MILESTONE_DAYS:
        xp += STREAK_MILESTONE_BONUS
    return xp


def level_progress(xp: int, level: int) -> dict:
    current = get_tier(level)
    nxt = next_tier(level)
    if not nxt:
        return {
            "current_level": level,
            "title": current.title,
            "xp": xp,
            "xp_into_level": xp - current.xp_required,
            "xp_to_next": 0,
            "progress_pct": 100,
            "next_level": None,
            "next_title": None,
        }
    span = nxt.xp_required - current.xp_required
    into = max(0, xp - current.xp_required)
    pct = min(100, int(into / span * 100)) if span else 100
    return {
        "current_level": level,
        "title": current.title,
        "xp": xp,
        "xp_into_level": into,
        "xp_to_next": max(0, nxt.xp_required - xp),
        "progress_pct": pct,
        "next_level": nxt.level,
        "next_title": nxt.title,
    }


def all_tiers_public() -> list[dict]:
    return [
        {
            "level": t.level,
            "title": t.title,
            "xp_required": t.xp_required,
            "perks": list(t.perks),
        }
        for t in LEVEL_TIERS
    ]


def xp_actions_public() -> list[dict]:
    return [
        {
            "action": key,
            "label": val.label,
            "xp": val.xp,
            "daily_max": val.daily_max,
            "daily_cap_xp": val.xp * val.daily_max,
        }
        for key, val in XP_ACTIONS.items()
    ]
