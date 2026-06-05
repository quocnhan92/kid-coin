from typing import Type, TypeVar
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Query

from app.core import context

T = TypeVar("T")


def get_family_id() -> str | None:
    return context.get_family_id()


def for_family(query: Query, model: Type[T], family_id: UUID) -> Query:
    if not hasattr(model, "family_id"):
        return query
    return query.filter(getattr(model, "family_id") == family_id)


def assert_same_family(resource_family_id: UUID, actor_family_id: UUID) -> None:
    if resource_family_id != actor_family_id:
        raise HTTPException(status_code=403, detail="Cross-family access denied")
