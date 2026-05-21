"""Read-only persona browsing — used by the persona-picker UI."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, status

from app.data.loader import get_seed

router = APIRouter(prefix="/guests", tags=["guests"])


@router.get("")
async def list_guests() -> list[dict[str, Any]]:
    """Return all demo personas."""
    return get_seed("guests")


@router.get("/{guest_id}")
async def get_guest(guest_id: str) -> dict[str, Any]:
    """Return a single persona by id."""
    for guest in get_seed("guests"):
        if guest.get("id") == guest_id:
            return guest
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Guest not found"
    )
