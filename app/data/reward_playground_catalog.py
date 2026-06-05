"""Reward Playground — fun games unlocked by learning achievements."""

from __future__ import annotations

from typing import Any, Callable, Dict, List

RewardCheck = Callable[[Dict[str, Any]], bool]

ROLLout_LIVE = "live"
ROLLout_BETA = "beta"
ROLLout_DRAFT = "draft"

SESSION_CAP_DEFAULT = 600


def reward_flag_key(game_id: str) -> str:
    return f"play.reward.{game_id}"


def _g(
    *,
    id: str,
    title: str,
    title_vi: str,
    emoji: str,
    route: str,
    color: str,
    desc_en: str,
    desc_vi: str,
    rule_key: str,
    genre: str,
    player_mode: str = "solo",
    rollout_status: str = ROLLout_DRAFT,
    co_op_parent: bool = False,
    session_cap_seconds: int = SESSION_CAP_DEFAULT,
) -> Dict[str, Any]:
    return {
        "id": id,
        "title": title,
        "title_vi": title_vi,
        "emoji": emoji,
        "route": route,
        "color": color,
        "desc_en": desc_en,
        "desc_vi": desc_vi,
        "rule_key": rule_key,
        "genre": genre,
        "player_mode": player_mode,
        "rollout_status": rollout_status,
        "co_op_parent": co_op_parent,
        "session_cap_seconds": session_cap_seconds,
    }


REWARD_GAMES: List[Dict[str, Any]] = [
    _g(
        id="snake",
        title="Snake Hunt",
        title_vi="Rắn săn mồi",
        emoji="🐍",
        route="/game/snake",
        color="green",
        desc_en="Eat food, grow long — classic reflex fun.",
        desc_vi="Ăn mồi, rắn dài ra",
        rule_key="snake",
        genre="reflex",
        rollout_status=ROLLout_LIVE,
    ),
    _g(
        id="2048",
        title="2048",
        title_vi="2048",
        emoji="🔢",
        route="/game/2048",
        color="amber",
        desc_en="Merge tiles to reach 2048.",
        desc_vi="Gộp số đến 2048",
        rule_key="2048",
        genre="puzzle",
        rollout_status=ROLLout_LIVE,
    ),
    _g(
        id="memory",
        title="Memory Match",
        title_vi="Lật bài nhớ",
        emoji="🃏",
        route="/game/memory",
        color="cyan",
        desc_en="Classic flip-card memory — pure fun.",
        desc_vi="Lật bài gốc — giải trí thuần",
        rule_key="memory",
        genre="puzzle",
        rollout_status=ROLLout_LIVE,
    ),
    _g(
        id="flappy",
        title="Flappy Coin",
        title_vi="Gà Bay",
        emoji="🐦",
        route="/game/flappy",
        color="pink",
        desc_en="Tap to fly through pipes.",
        desc_vi="Chạm để bay qua ống",
        rule_key="flappy",
        genre="reflex",
        rollout_status=ROLLout_LIVE,
    ),
    _g(
        id="block_breaker",
        title="Block Breaker",
        title_vi="Phá gạch",
        emoji="🧱",
        route="/game/block-breaker",
        color="red",
        desc_en="Break all bricks with the ball.",
        desc_vi="Phá hết gạch bằng bóng",
        rule_key="block_breaker",
        genre="reflex",
        rollout_status=ROLLout_LIVE,
    ),
    _g(
        id="hextris",
        title="Hextris",
        title_vi="Xoay khối",
        emoji="⬡",
        route="/game/hextris",
        color="purple",
        desc_en="Rotate the hex, match colors — fast reflex.",
        desc_vi="Xoay hex, ghép màu — phản xạ nhanh",
        rule_key="hextris",
        genre="reflex",
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="pong_2p",
        title="Pong 2P",
        title_vi="Pong 2 người",
        emoji="🏓",
        route="/game/pong-2p",
        color="lime",
        desc_en="Classic paddle duel — play with a parent.",
        desc_vi="Đấu vợt cổ điển — chơi cùng bố mẹ",
        rule_key="pong_2p",
        genre="co_op",
        player_mode="local_2p",
        co_op_parent=True,
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="snake_2p",
        title="Snake 2P",
        title_vi="Rắn 2 người",
        emoji="🐍",
        route="/game/snake-2p",
        color="green",
        desc_en="Two snakes, one screen — co-op or versus.",
        desc_vi="Hai rắn một màn — chơi cùng bố mẹ",
        rule_key="snake_2p",
        genre="co_op",
        player_mode="local_2p",
        co_op_parent=True,
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="minesweeper",
        title="Minesweeper",
        title_vi="Dò mìn",
        emoji="💣",
        route="/game/minesweeper",
        color="slate",
        desc_en="Clear the field without hitting mines.",
        desc_vi="Dò mìn an toàn",
        rule_key="minesweeper",
        genre="puzzle",
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="air_hockey_2p",
        title="Air Hockey 2P",
        title_vi="Khúc côn cầu 2 người",
        emoji="🏒",
        route="/game/air-hockey-2p",
        color="sky",
        desc_en="Fast puck action — local 2-player.",
        desc_vi="Đánh puck nhanh — 2 người một màn",
        rule_key="air_hockey_2p",
        genre="co_op",
        player_mode="local_2p",
        co_op_parent=True,
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="ohh1",
        title="0h h1",
        title_vi="0h h1",
        emoji="🟥",
        route="/game/ohh1",
        color="rose",
        desc_en="Fill rows and columns — logic puzzle.",
        desc_vi="Lấp hàng cột — giải đố logic",
        rule_key="ohh1",
        genre="puzzle",
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="ohn0",
        title="0h n0",
        title_vi="0h n0",
        emoji="⬛",
        route="/game/ohn0",
        color="stone",
        desc_en="Mark squares carefully — no three in a row.",
        desc_vi="Đánh dấu ô — không ba liên tiếp",
        rule_key="ohn0",
        genre="puzzle",
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="reversi",
        title="Reversi",
        title_vi="Cờ lật",
        emoji="⚫",
        route="/game/reversi",
        color="indigo",
        desc_en="Flip discs to control the board.",
        desc_vi="Lật quân chiếm bàn",
        rule_key="reversi",
        genre="strategy",
        player_mode="local_2p",
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="tower_defense_lite",
        title="Tower Defense",
        title_vi="Phòng thủ tháp",
        emoji="🏰",
        route="/game/tower-defense",
        color="orange",
        desc_en="Place towers, stop the waves.",
        desc_vi="Đặt tháp, chặn đợt quái",
        rule_key="tower_defense_lite",
        genre="strategy",
        rollout_status=ROLLout_BETA,
    ),
    _g(
        id="rhythm_trainer",
        title="Rhythm Trainer",
        title_vi="Luyện nhịp",
        emoji="🎵",
        route="/game/rhythm-trainer",
        color="violet",
        desc_en="Tap to the beat — music mini-game.",
        desc_vi="Chạm theo nhịp — mini game âm nhạc",
        rule_key="rhythm_trainer",
        genre="music",
        rollout_status=ROLLout_DRAFT,
    ),
    _g(
        id="paint_sandbox",
        title="Paint Sandbox",
        title_vi="Vẽ tự do",
        emoji="🎨",
        route="/game/paint-sandbox",
        color="fuchsia",
        desc_en="Draw and doodle freely.",
        desc_vi="Vẽ và nguệch ngoạc tự do",
        rule_key="paint_sandbox",
        genre="creative",
        rollout_status=ROLLout_DRAFT,
    ),
]

REWARD_GAME_BY_ID: Dict[str, Dict[str, Any]] = {g["id"]: g for g in REWARD_GAMES}

REWARD_SECTIONS: List[Dict[str, Any]] = [
    {
        "key": "reflex",
        "title_en": "Reflex",
        "title_vi": "Phản xạ",
        "game_ids": ["hextris", "flappy", "snake", "block_breaker"],
    },
    {
        "key": "co_op",
        "title_en": "Play with parents",
        "title_vi": "Chơi cùng bố mẹ",
        "game_ids": ["pong_2p", "snake_2p", "air_hockey_2p"],
        "section_flag": "play.reward.co_op_hub",
    },
    {
        "key": "puzzle",
        "title_en": "Puzzles",
        "title_vi": "Giải đố",
        "game_ids": ["minesweeper", "2048", "memory", "ohh1", "ohn0"],
    },
    {
        "key": "strategy",
        "title_en": "Strategy",
        "title_vi": "Chiến thuật",
        "game_ids": ["reversi", "tower_defense_lite"],
    },
    {
        "key": "creative",
        "title_en": "Creative & Music",
        "title_vi": "Sáng tạo & Âm nhạc",
        "game_ids": ["rhythm_trainer", "paint_sandbox"],
    },
]

VISIBLE_ROLLOUT = frozenset({ROLLout_BETA, ROLLout_LIVE})
ALL_ROLLOUT = frozenset({ROLLout_DRAFT, ROLLout_BETA, ROLLout_LIVE})


def _rule_snake(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 1 or m.get("english_themes_done", 0) >= 1


def _rule_2048(m: Dict[str, Any]) -> bool:
    return m.get("math_sessions_3star", 0) >= 1 or m.get("english_themes_done", 0) >= 1


def _rule_memory(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 2


def _rule_flappy(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 3 or m.get("avg_mastery_score", 0) >= 0.5


def _rule_block_breaker(m: Dict[str, Any]) -> bool:
    return m.get("english_themes_done", 0) >= 2 or m.get("skills_mastered_count", 0) >= 5


def _rule_hextris(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 2


def _rule_pong_2p(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 1


def _rule_snake_2p(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 1


def _rule_minesweeper(m: Dict[str, Any]) -> bool:
    return m.get("math_sessions_3star", 0) >= 1


def _rule_air_hockey_2p(m: Dict[str, Any]) -> bool:
    return m.get("english_themes_done", 0) >= 1


def _rule_ohh1(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 3


def _rule_ohn0(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 3


def _rule_reversi(m: Dict[str, Any]) -> bool:
    return m.get("avg_mastery_score", 0) >= 0.5


def _rule_tower_defense_lite(m: Dict[str, Any]) -> bool:
    return m.get("english_themes_done", 0) >= 2


def _rule_rhythm_trainer(m: Dict[str, Any]) -> bool:
    return m.get("skills_mastered_count", 0) >= 5


def _rule_paint_sandbox(m: Dict[str, Any]) -> bool:
    return m.get("english_themes_done", 0) >= 1 or m.get("skills_mastered_count", 0) >= 2


RULES: Dict[str, RewardCheck] = {
    "snake": _rule_snake,
    "2048": _rule_2048,
    "memory": _rule_memory,
    "flappy": _rule_flappy,
    "block_breaker": _rule_block_breaker,
    "hextris": _rule_hextris,
    "pong_2p": _rule_pong_2p,
    "snake_2p": _rule_snake_2p,
    "minesweeper": _rule_minesweeper,
    "air_hockey_2p": _rule_air_hockey_2p,
    "ohh1": _rule_ohh1,
    "ohn0": _rule_ohn0,
    "reversi": _rule_reversi,
    "tower_defense_lite": _rule_tower_defense_lite,
    "rhythm_trainer": _rule_rhythm_trainer,
    "paint_sandbox": _rule_paint_sandbox,
}

RULE_HINTS: Dict[str, str] = {
    "snake": "1 mastery skill ≥70% OR 1 English theme",
    "2048": "1 Math session ★★★ OR 1 English theme",
    "memory": "2 mastery skills ≥70%",
    "flappy": "3 mastery skills OR avg mastery ≥50%",
    "block_breaker": "2 English themes OR 5 mastery skills",
    "hextris": "2 mastery skills ≥70%",
    "pong_2p": "1 mastery skill ≥70%",
    "snake_2p": "1 mastery skill ≥70%",
    "minesweeper": "1 Math session ★★★",
    "air_hockey_2p": "1 English theme completed",
    "ohh1": "3 mastery skills ≥70%",
    "ohn0": "3 mastery skills ≥70%",
    "reversi": "Average mastery score ≥50%",
    "tower_defense_lite": "2 English themes completed",
    "rhythm_trainer": "5 mastery skills ≥70%",
    "paint_sandbox": "1 English theme OR 2 mastery skills",
}
