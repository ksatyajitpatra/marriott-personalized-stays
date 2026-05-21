"""Mock persona auth — login/logout/me/profile.

Three personas are accepted: alex, jordan, sam (PRD Section 4).
Sessions are stored in a signed cookie via Starlette's SessionMiddleware.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.dependencies import get_session_guest_id, require_guest
from app.models.auth import (
    GuestSummary,
    LoginRequest,
    SessionResponse,
    UpdatePreferencesRequest,
    build_guest_summary,
)
from app.services import guest_preference_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _find_guest(guest_id: str) -> dict[str, Any] | None:
    """Look up a persona seed dict by id (includes preference overrides)."""
    return guest_preference_service.get_guest_record(guest_id)


@router.post("/login", response_model=SessionResponse)
async def login(request: Request, body: LoginRequest) -> SessionResponse:
    """Set the session cookie to the requested persona id."""
    guest = _find_guest(body.guest_id)
    if guest is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found"
        )
    request.session["guest_id"] = body.guest_id
    return SessionResponse(authenticated=True, guest=build_guest_summary(guest))


@router.post("/logout", response_model=SessionResponse)
async def logout(request: Request) -> SessionResponse:
    """Clear the session cookie."""
    request.session.clear()
    return SessionResponse(authenticated=False, guest=None)


@router.get("/me", response_model=SessionResponse)
async def me(request: Request) -> SessionResponse:
    """Return the currently logged-in persona, if any."""
    guest_id = get_session_guest_id(request)
    if not guest_id:
        return SessionResponse(authenticated=False, guest=None)

    guest = _find_guest(guest_id)
    if guest is None:
        request.session.clear()
        return SessionResponse(authenticated=False, guest=None)
    return SessionResponse(authenticated=True, guest=build_guest_summary(guest))


@router.get("/profile")
async def profile(guest: GuestSummary = Depends(require_guest)) -> dict[str, Any]:
    """Return the full guest profile (preferences, pets, badges, etc.)."""
    full = _find_guest(guest.id)
    if full is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found"
        )
    return full


@router.patch("/profile/preferences")
async def update_preferences(
    body: UpdatePreferencesRequest,
    guest: GuestSummary = Depends(require_guest),
) -> dict[str, Any]:
    """Update mutable guest preferences (e.g. pet service search radius)."""
    try:
        return guest_preference_service.update_preferences(
            guest.id, body.model_dump(exclude_unset=True)
        )
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found"
        ) from None
