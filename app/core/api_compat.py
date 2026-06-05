from typing import Optional, Tuple

from fastapi import HTTPException, Request

API_VERSION = "1"
MIN_SUPPORTED_CLIENT = "1.0.0"


def parse_client_version(request: Request) -> Optional[str]:
    return request.headers.get("X-Client-Version") or request.headers.get("X-App-Version")


def compare_versions(a: str, b: str) -> int:
    def parts(v: str) -> Tuple[int, ...]:
        out = []
        for piece in v.split("."):
            try:
                out.append(int(piece))
            except ValueError:
                out.append(0)
        return tuple(out)

    pa, pb = parts(a), parts(b)
    length = max(len(pa), len(pb))
    pa = pa + (0,) * (length - len(pa))
    pb = pb + (0,) * (length - len(pb))
    if pa < pb:
        return -1
    if pa > pb:
        return 1
    return 0


def check_client_version(request: Request, min_required: str = MIN_SUPPORTED_CLIENT) -> None:
    client = parse_client_version(request)
    if not client:
        return
    if compare_versions(client, min_required) < 0:
        raise HTTPException(
            status_code=426,
            detail=f"Client version {client} is below minimum {min_required}",
        )


def apply_api_headers(response, *, deprecated: bool = False, sunset: Optional[str] = None):
    response.headers["X-API-Version"] = API_VERSION
    if deprecated:
        response.headers["Deprecation"] = "true"
    if sunset:
        response.headers["Sunset"] = sunset
    return response
