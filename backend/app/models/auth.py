"""Auth + persona schemas.

Mock auth: three hardcoded personas (alex, jordan, sam) per PRD Section 4.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Login payload — only the three demo personas are accepted."""

    guest_id: str = Field(pattern=r"^(alex|jordan|sam)$")


class GuestSummary(BaseModel):
    """Lightweight guest payload returned on login / `/auth/me`."""

    id: str
    name: str
    email: str
    bonvoy_id: str
    tier: str
    tier_color: str
    points: int


class SessionResponse(BaseModel):
    """`/auth/me` and `/auth/login` response wrapper."""

    authenticated: bool
    guest: GuestSummary | None = None


class UpdatePreferencesRequest(BaseModel):
    """Partial preference updates from the profile UI."""

    dietary: list[str] | None = None
    interests: list[str] | None = None
    pet_service_categories: list[str] | None = None
    pet_service_radius_miles: float | None = Field(
        default=None, ge=1, le=50, description="Pet service search radius in miles"
    )


def build_guest_summary(guest: dict[str, Any]) -> GuestSummary:
    """Project a raw guest seed dict into the public summary shape.

    Centralised here so every router/dependency uses the same fields.
    """
    return GuestSummary(
        id=guest["id"],
        name=guest["name"],
        email=guest["email"],
        bonvoy_id=guest["bonvoy_id"],
        tier=guest["tier"],
        tier_color=guest["tier_color"],
        points=guest["points"],
    )
