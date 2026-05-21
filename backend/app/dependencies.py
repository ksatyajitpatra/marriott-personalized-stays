"""Shared FastAPI dependencies (mock auth helpers)."""

from __future__ import annotations

from fastapi import HTTPException, Request, status

from app.data.loader import get_seed
from app.models.auth import GuestSummary, build_guest_summary


def get_session_guest_id(request: Request) -> str | None:
    """Return the guest_id stored on the session cookie, if any."""
    return request.session.get("guest_id")


async def require_guest(request: Request) -> GuestSummary:
    """Require an authenticated persona; raise 401 otherwise.

    Args:
        request: Starlette request (carries the session cookie).

    Returns:
        A `GuestSummary` for the logged-in persona.

    Raises:
        HTTPException: 401 if no session, or session points at a missing guest.
    """
    guest_id = get_session_guest_id(request)
    if not guest_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    for guest in get_seed("guests"):
        if guest.get("id") == guest_id:
            return build_guest_summary(guest)

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid session",
    )
