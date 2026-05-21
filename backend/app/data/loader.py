"""Tiny in-memory loader for static JSON seed data.

The PRD ships with hand-curated JSON in `/data/seeds/`. The backend reads
them once at startup and exposes them as immutable Python objects via
`get_seed(name)`.

We intentionally avoid sqlite/postgres here — the demo's data plane is
read-mostly, and keeping it as JSON makes it trivial for teammates to
edit a hotel's eco numbers without writing migrations.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Module-level store. Populated once on startup and read everywhere else.
_seed_store: dict[str, Any] = {}


def load_seeds(seeds_path: str | Path) -> None:
    """Load every `*.json` file in the seeds directory into memory.

    The file name (without extension) becomes the seed key, e.g.
    `hotels.json` is reachable as `get_seed("hotels")`.

    Args:
        seeds_path: Directory containing the seed JSON files. Resolved
            against the current working directory if relative.

    Raises:
        FileNotFoundError: If the directory does not exist.
    """
    base = Path(seeds_path).resolve()
    if not base.is_dir():
        raise FileNotFoundError(f"Seed directory not found: {base}")

    _seed_store.clear()
    for seed_file in sorted(base.glob("*.json")):
        with seed_file.open(encoding="utf-8") as handle:
            _seed_store[seed_file.stem] = json.load(handle)
        logger.debug("Loaded seed '%s' (%d bytes)", seed_file.stem, seed_file.stat().st_size)

    logger.info("Loaded %d seed file(s) from %s", len(_seed_store), base)


def get_seed(name: str) -> Any:
    """Return the parsed JSON for a seed by name.

    Args:
        name: Seed key (filename without `.json`).

    Returns:
        Whatever JSON the file contained — typically a list[dict] or dict.

    Raises:
        KeyError: If the seed has not been loaded.
    """
    if name not in _seed_store:
        raise KeyError(
            f"Seed '{name}' not loaded. Available: {sorted(_seed_store)}"
        )
    return _seed_store[name]


def has_seed(name: str) -> bool:
    """Return True if the named seed is loaded."""
    return name in _seed_store
