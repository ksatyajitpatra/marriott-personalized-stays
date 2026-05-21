"""Weather service — OpenWeatherMap with a deterministic mock fallback.

The PRD allows live weather (OWM free tier) but ships a mock so the demo
runs offline and without keys. The mock generates a realistic 3-day stub
using the city name as a seed.
"""

from __future__ import annotations

import hashlib
import logging
from datetime import date, timedelta
from typing import Any

import httpx

from app.config import settings
from app.models.arrival_brief import WeatherDay

logger = logging.getLogger(__name__)

_OWM_GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
_OWM_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"


# --- Mock generator ---------------------------------------------------------


def _seed_int(s: str) -> int:
    """Produce a stable integer from a city name for deterministic mocks."""
    return int(hashlib.sha1(s.encode()).hexdigest(), 16)


_ICONS = ["sun", "partly", "cloud", "rain"]
_SUMMARIES = {
    "sun": "Sunny and pleasant",
    "partly": "Partly cloudy with sunny breaks",
    "cloud": "Mostly cloudy",
    "rain": "Light rain expected — bring a layer",
}


def _mock_forecast(city: str, check_in: str, check_out: str) -> list[WeatherDay]:
    """Deterministic 3-day forecast keyed by city name."""
    seed = _seed_int(city)
    try:
        start = date.fromisoformat(check_in)
        end = date.fromisoformat(check_out)
    except ValueError:
        return []
    n_days = max(1, min(5, (end - start).days))

    forecast: list[WeatherDay] = []
    for i in range(n_days):
        d = start + timedelta(days=i)
        # Vary highs around a city-specific baseline.
        base = 18 + (seed >> (i * 4)) % 12
        high = base + 6
        low = base - 2
        icon = _ICONS[(seed >> (i * 3)) % len(_ICONS)]
        forecast.append(
            WeatherDay(
                date=d.isoformat(),
                high_c=float(high),
                low_c=float(low),
                summary=_SUMMARIES[icon],
                icon=icon,
            )
        )
    return forecast


# --- Live OWM fetch --------------------------------------------------------


async def _live_forecast(
    city: str,
    check_in: str,
    check_out: str,
) -> list[WeatherDay] | None:
    """Fetch a real OWM 5-day/3-hour forecast and reduce it to daily highs/lows."""
    if not settings.openweather_api_key:
        return None

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            geo_resp = await client.get(
                _OWM_GEO_URL,
                params={"q": city, "limit": 1, "appid": settings.openweather_api_key},
            )
            geo_resp.raise_for_status()
            geo = geo_resp.json()
            if not geo:
                return None
            lat, lon = geo[0]["lat"], geo[0]["lon"]

            fc_resp = await client.get(
                _OWM_FORECAST_URL,
                params={
                    "lat": lat,
                    "lon": lon,
                    "units": "metric",
                    "appid": settings.openweather_api_key,
                },
            )
            fc_resp.raise_for_status()
            fc_data = fc_resp.json()
    except httpx.HTTPError as exc:
        logger.warning("OpenWeatherMap fetch failed for %s: %s", city, exc)
        return None

    return _reduce_owm_forecast(fc_data, check_in, check_out)


def _reduce_owm_forecast(
    fc_data: dict[str, Any],
    check_in: str,
    check_out: str,
) -> list[WeatherDay]:
    """Aggregate OWM 3-hour buckets into per-day highs/lows during the stay."""
    try:
        start = date.fromisoformat(check_in)
        end = date.fromisoformat(check_out)
    except ValueError:
        return []

    by_day: dict[str, dict[str, Any]] = {}
    for entry in fc_data.get("list", []):
        try:
            dt = date.fromtimestamp(entry["dt"])
        except (KeyError, OSError, ValueError):
            continue
        if dt < start or dt >= end:
            continue
        bucket = by_day.setdefault(
            dt.isoformat(),
            {"high": -999.0, "low": 999.0, "icons": []},
        )
        main = entry.get("main", {})
        bucket["high"] = max(bucket["high"], main.get("temp_max", main.get("temp", 0)))
        bucket["low"] = min(bucket["low"], main.get("temp_min", main.get("temp", 0)))
        weather = (entry.get("weather") or [{}])[0]
        bucket["icons"].append(weather.get("main", "Clouds"))

    out: list[WeatherDay] = []
    for d, bucket in sorted(by_day.items()):
        icon = _owm_icon_to_key(bucket["icons"])
        out.append(
            WeatherDay(
                date=d,
                high_c=round(bucket["high"], 1),
                low_c=round(bucket["low"], 1),
                summary=_SUMMARIES[icon],
                icon=icon,
            )
        )
    return out


def _owm_icon_to_key(weather_main_list: list[str]) -> str:
    """Pick a single icon from the 3-hour observations of a day."""
    counts = {"sun": 0, "partly": 0, "cloud": 0, "rain": 0}
    for w in weather_main_list:
        if w == "Clear":
            counts["sun"] += 1
        elif w in ("Rain", "Drizzle", "Thunderstorm"):
            counts["rain"] += 1
        elif w == "Clouds":
            counts["partly"] += 1
        else:
            counts["cloud"] += 1
    return max(counts, key=lambda k: counts[k])


# --- Public entry point ----------------------------------------------------


async def get_forecast(city: str, check_in: str, check_out: str) -> list[WeatherDay]:
    """Return the forecast for a stay, preferring live data when configured."""
    live = await _live_forecast(city, check_in, check_out)
    if live:
        return live
    return _mock_forecast(city, check_in, check_out)
