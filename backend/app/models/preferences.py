"""Allowed guest preference values (PRD Section 6.1)."""

from __future__ import annotations

DIETARY_OPTIONS: tuple[str, ...] = (
    "vegetarian",
    "vegan",
    "halal",
    "kosher",
    "gluten_free",
    "nut_allergy",
)

INTEREST_OPTIONS: tuple[str, ...] = (
    "culture",
    "food",
    "outdoor",
    "nightlife",
    "sustainability",
    "wellness",
)

PET_SERVICE_CATEGORY_OPTIONS: tuple[str, ...] = (
    "dog_walker",
    "mobile_grooming",
)

# Map hotel seed `city` to restaurants.json keys
CITY_RESTAURANT_KEYS: dict[str, str] = {
    "New York": "new_york",
    "Washington": "washington_dc",
    "Chicago": "chicago",
    "Miami": "miami",
}
