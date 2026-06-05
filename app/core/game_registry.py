import logging
from typing import Callable, Optional, Set

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.play import PlayGame
from app.services.platform_seed import sync_play_game_routes

logger = logging.getLogger(__name__)

_registered_paths: Set[str] = set()


def register_game_routes(app: FastAPI, render_page: Callable) -> int:
    db: Session = SessionLocal()
    count = 0
    try:
        sync_play_game_routes(db)
        db.commit()
        games = (
            db.query(PlayGame)
            .filter(
                PlayGame.is_active == True,
                PlayGame.ssr_template.isnot(None),
                PlayGame.launch_url.isnot(None),
            )
            .all()
        )
        for game in games:
            path = game.launch_url.rstrip("/") if game.launch_url else None
            template = game.ssr_template
            if not path or not template or path in _registered_paths:
                continue
            _mount_game_route(
                app, path, template, render_page, requires_wallet=bool(game.requires_wallet)
            )
            _registered_paths.add(path)
            count += 1
            logger.info("Game registry: mounted %s -> %s", path, template)
    finally:
        db.close()
    return count


def _mount_game_route(
    app: FastAPI,
    path: str,
    template: str,
    render_page: Callable,
    requires_wallet: bool = False,
) -> None:
    async def handler(request: Request, _template: str = template):
        if requires_wallet:
            from app.core.reward_route_guard import reward_route_guard

            blocked = reward_route_guard(request)
            if blocked:
                return blocked
        return render_page(request, _template)

    app.add_api_route(
        path,
        handler,
        methods=["GET"],
        response_class=HTMLResponse,
        include_in_schema=False,
        name=f"game_registry_{path.replace('/', '_')}",
    )


def register_legacy_redirects(app: FastAPI) -> None:
    redirects = {
        "/game/math-blast": "/game/math-blast-v2",
    }
    for src, dst in redirects.items():
        if src in _registered_paths:
            continue

        async def _redirect(_request: Request, target: str = dst):
            return RedirectResponse(url=target, status_code=301)

        app.add_api_route(
            src,
            _redirect,
            methods=["GET"],
            include_in_schema=False,
        )
