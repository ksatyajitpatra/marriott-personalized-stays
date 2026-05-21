"""FastAPI application entrypoint.

Wires up:
  * lifespan hook (loads seed JSON, seeds reservations, warms LLM cache)
  * CORS middleware for the Next.js frontend
  * SessionMiddleware for the mock persona auth
  * All routers
"""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.config import settings
from app.data.loader import load_seeds
from app.routers import (
    affiliate,
    arrival_brief,
    arrival_brief_stream,
    auth,
    guests,
    health,
    hotels,
    partners,
    reservations,
)
from app.services import reservation_service
from app.services.hotel_content_service import warm_hotel_content_cache

logger = logging.getLogger("uvicorn.error")


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Run startup/shutdown work for the API."""
    logger.info("Loading seed data from %s", settings.seeds_path)
    load_seeds(settings.seeds_path)

    logger.info("Initializing in-memory reservation store from seeds")
    reservation_service.init_reservations_from_seeds()

    logger.info(
        "Warming hotel content cache (use_mock_llm=%s)", settings.use_mock_llm
    )
    await warm_hotel_content_cache()

    logger.info("Backend ready")
    yield
    logger.info("Backend shutting down")


app = FastAPI(
    title="Marriott Bonvoy Enhanced Experience API",
    description=(
        "Additive backend for the Bonvoy enhanced experience demo. "
        "All data is mocked — no real Marriott APIs are touched."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cookie-based session for mock persona auth. https_only=False because
# the demo runs on plain http://localhost.
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.session_secret,
    same_site="lax",
    https_only=False,
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(guests.router)
app.include_router(hotels.router)
app.include_router(partners.router)
app.include_router(reservations.router)
app.include_router(arrival_brief.router)
app.include_router(arrival_brief_stream.router)
app.include_router(affiliate.router)
