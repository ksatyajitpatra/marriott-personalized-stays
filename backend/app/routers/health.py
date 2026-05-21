"""Liveness probe."""

from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Return a static OK payload for k8s/docker healthchecks."""
    return {"status": "ok"}
