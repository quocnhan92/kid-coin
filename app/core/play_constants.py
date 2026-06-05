"""Play Hub — game ids & wallet account codes (sổ cái)."""

# Learning games (điểm / tiến độ tách riêng)
GAME_MATH_VN = "math_blast"
GAME_MATH_EN = "english_math"
GAME_ENGLISH_SHOOTER = "english_shooter"

LEARNING_GAME_IDS = frozenset({GAME_MATH_VN, GAME_MATH_EN, GAME_ENGLISH_SHOOTER})

# Tài khoản sổ cái — chỉ 2 tài khoản hệ thống cố định; mỗi game học = EARN:{game_id} (JSONB, không cần ALTER TABLE)
ACCOUNT_AVAILABLE = "WALLET_AVAILABLE"
ACCOUNT_SPEND_REWARD = "SPEND_REWARD_PLAY"
EARN_ACCOUNT_PREFIX = "EARN:"

# Alias cũ (đọc ví legacy) → mã mới
LEGACY_EARN_ACCOUNTS = {
    "EARN_MATH_VN": f"{EARN_ACCOUNT_PREFIX}{GAME_MATH_VN}",
    "EARN_MATH_EN": f"{EARN_ACCOUNT_PREFIX}{GAME_MATH_EN}",
    "EARN_ENGLISH_SHOOTER": f"{EARN_ACCOUNT_PREFIX}{GAME_ENGLISH_SHOOTER}",
}


def earn_account_for_game(game_id: str) -> str:
    """Mỗi play_games.id một tài khoản earn — thêm game mới không sửa schema DB."""
    return f"{EARN_ACCOUNT_PREFIX}{game_id}"

# 1 câu đúng (học) → 1 điểm vào quỹ chi tiêu giải trí
POINTS_PER_CORRECT = 1

# Chi phí 1 lượt chơi game phần thưởng (availableBalance)
REWARD_PLAY_COST: dict[str, int] = {
    "snake": 5,
    "2048": 8,
    "memory": 6,
    "flappy": 10,
    "block_breaker": 12,
    "hextris": 6,
    "pong_2p": 4,
    "snake_2p": 5,
    "minesweeper": 7,
    "air_hockey_2p": 6,
    "ohh1": 8,
    "ohn0": 8,
    "reversi": 9,
    "tower_defense_lite": 10,
    "rhythm_trainer": 8,
    "paint_sandbox": 5,
}
