from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class FeatureFlagItem(BaseModel):
    key: str
    enabled: bool


class FeaturesResponse(BaseModel):
    flags: Dict[str, bool]
    api_version: str = "1"
    min_client_version: str = "1.0.0"


class PublicGameItem(BaseModel):
    id: str
    display_name: str
    game_type: str
    hub_zone: str = "learning"
    subject: Optional[str] = None
    grade_min: int = 1
    grade_max: int = 5
    launch_url: Optional[str] = None
    icon: Optional[str] = None
    tagline: Optional[str] = None
    min_client_version: str = "1.0.0"
    requires_wallet: bool = False


class PublicGamesResponse(BaseModel):
    games: List[PublicGameItem]


class FeatureFlagAdminItem(BaseModel):
    key: str
    enabled: bool
    scope: str
    scope_value: Optional[str] = None
    description: Optional[str] = None
    metadata: Dict[str, Any] = {}


class FeatureFlagUpdateRequest(BaseModel):
    enabled: bool
    scope: str = "global"
    scope_value: Optional[str] = None
    description: Optional[str] = None
