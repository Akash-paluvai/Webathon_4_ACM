"""
GeoNames Geo Service — Resolves region names to lat/lon coordinates.

Uses GEONAMES_USERNAME from .env.
Caches results indefinitely (coordinates don't change).
Falls back to hardcoded coordinates on any failure.
"""

import os
import time
from typing import Dict, Optional, Tuple

# ── Hardcoded fallback coordinates ──
FALLBACK_COORDS: Dict[str, Tuple[float, float]] = {
    "North America": (40.7128, -74.0060),     # New York
    "Europe": (51.5074, -0.1278),             # London
    "East Asia": (35.6762, 139.6503),         # Tokyo
    "South Asia": (19.0760, 72.8777),         # Mumbai
    "Latin America": (-23.5505, -46.6333),    # São Paulo
    "Middle East": (25.2048, 55.2708),        # Dubai
    "Africa": (-1.2921, 36.8219),             # Nairobi
    "Southeast Asia": (1.3521, 103.8198),     # Singapore
    "Oceania": (-33.8688, 151.2093),          # Sydney
    "Central Asia": (41.2995, 69.2401),       # Tashkent
    # Indian states / cities
    "Telangana": (17.3850, 78.4867),
    "Maharashtra": (19.0760, 72.8777),
    "Tamil Nadu": (13.0827, 80.2707),
    "Karnataka": (12.9716, 77.5946),
    "Andhra Pradesh": (15.9129, 79.7400),
    "Kerala": (10.8505, 76.2711),
    "West Bengal": (22.5726, 88.3639),
    "Delhi": (28.7041, 77.1025),
    "Uttar Pradesh": (26.8467, 80.9462),
}

# ── Cache (persists for process lifetime) ──
_geo_cache: Dict[str, Tuple[float, float]] = {}


def _get_username() -> Optional[str]:
    return os.environ.get("GEONAMES_USERNAME", "").strip() or None


def fetch_coordinates(place_name: str) -> Tuple[float, float]:
    """
    Resolve a place name to (lat, lon).

    Uses GeoNames API with fallback to hardcoded coordinates.
    Results are cached indefinitely.
    """
    # Check cache first
    if place_name in _geo_cache:
        return _geo_cache[place_name]

    # Check fallback dict
    if place_name in FALLBACK_COORDS:
        _geo_cache[place_name] = FALLBACK_COORDS[place_name]
        return FALLBACK_COORDS[place_name]

    # Try GeoNames API
    username = _get_username()
    if username:
        try:
            import httpx
            resp = httpx.get(
                "http://api.geonames.org/searchJSON",
                params={
                    "q": place_name,
                    "maxRows": 1,
                    "username": username,
                },
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                geonames = data.get("geonames", [])
                if geonames:
                    lat = float(geonames[0]["lat"])
                    lon = float(geonames[0]["lng"])
                    _geo_cache[place_name] = (lat, lon)
                    return (lat, lon)
        except Exception:
            pass

    # Final fallback — return (0, 0) or closest match
    _geo_cache[place_name] = (0.0, 0.0)
    return (0.0, 0.0)


def fetch_coordinates_batch(regions: list) -> Dict[str, Tuple[float, float]]:
    """Resolve multiple regions to coordinates."""
    return {region: fetch_coordinates(region) for region in regions}


def get_all_fallback_coords() -> Dict[str, Tuple[float, float]]:
    """Get all hardcoded coordinates (useful for offline mode)."""
    return dict(FALLBACK_COORDS)
