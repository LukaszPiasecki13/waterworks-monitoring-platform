"""Schemas returned by future business-owned audit endpoints."""

from datetime import datetime
from typing import Any

from pydantic import ConfigDict, Field

from app.core.schemas import BaseSchema


class AuditHistoryQuery(BaseSchema):
    """Pagination query parameters for entity audit history endpoints."""

    limit: int = Field(100, ge=1, le=200)
    offset: int = Field(0, ge=0)


class AuditEventResponse(BaseSchema):
    model_config = ConfigDict(from_attributes=True)

    id: int
    entity_type: str
    entity_id: str
    action: str
    actor_id: str
    actor_display_name: str | None
    context_type: str | None
    context_id: str | None
    changes: dict[str, Any]
    created_at: datetime
