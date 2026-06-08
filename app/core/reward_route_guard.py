"""SSR gate — reward-zone games must enter via Reward Playground."""
from fastapi import Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.play import PlayGame

REWARD_GAME_PATHS = {
    "/game/snake": "snake",
    "/game/2048": "2048",
    "/game/flappy": "flappy_classic",
    "/game/block-breaker": "block_breaker",
    "/game/memory": "memory",
    "/game/hextris": "hextris",
    "/game/pong-2p": "pong_2p",
    "/game/snake-2p": "snake_2p",
    "/game/minesweeper": "minesweeper",
    "/game/air-hockey-2p": "air_hockey_2p",
    "/game/ohh1": "ohh1",
    "/game/ohn0": "ohn0",
    "/game/reversi": "reversi",
    "/game/tower-defense": "tower_defense_lite",
    "/game/rhythm-trainer": "rhythm_trainer",
    "/game/paint-sandbox": "paint_sandbox",
    "/game/connect4-2p": "connect4_2p",
    "/game/tic-tac-toe-2p": "tic_tac_toe_2p",
    "/game/coop-catch-2p": "coop_catch_2p",
    "/game/memory-duel-2p": "memory_duel_2p",
    "/game/bubble-pop-2p": "bubble_pop_2p",
    "/game/checkers-lite-2p": "checkers_lite_2p",
    "/game/maze-race-2p": "maze_race_2p",
    "/game/draw-guess-2p": "draw_guess_2p",
    "/game/rhythm-duel-2p": "rhythm_duel_2p",
    "/game/gomoku-lite-2p": "gomoku_lite_2p",
}


def reward_route_guard(request: Request) -> Response | None:
    if settings.PLAY_TEST_UNLOCK_ALL:
        return None
    path = request.url.path.rstrip("/") or "/"
    game_id = REWARD_GAME_PATHS.get(path)
    if not game_id:
        return None
    from app.core.database import SessionLocal

    db: Session = SessionLocal()
    try:
        game = db.query(PlayGame).filter(PlayGame.id == game_id).first()
        if game and game.hub_zone == "reward" and game.requires_wallet:
            return RedirectResponse(url="/game/rewards?gate=1", status_code=302)
    finally:
        db.close()
    return None
