"""
Phase 8 Kaggle Movies Box Office data loader.

Loads the REAL Kaggle Movies Box Office Dataset (2000-2024) — 5,000 films.
Downloaded via kagglehub from aditya126/movies-box-office-dataset-2000-2024.

Columns in the real dataset:
  Rank, Release Group, $Worldwide, $Domestic, Domestic %, $Foreign, Foreign %,
  Year, Genres, Rating, Vote_Count, Original_Language, Production_Countries

This module is purely additive — no existing files or endpoints are modified.
"""

from __future__ import annotations

import csv
import os
import re
from dataclasses import dataclass
from typing import List, Optional

_DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
_CSV_PATH = os.path.join(_DATA_DIR, "kaggle_boxoffice_raw.csv")


# ─────────────────────────────────────────────────
# Data model
# ─────────────────────────────────────────────────

@dataclass
class BoxOfficeRecord:
    title: str
    year: int
    genres: List[str]
    budget: int                 # estimated from worldwide gross (no budget in Kaggle)
    worldwide_gross: int
    domestic_gross: int
    opening_weekend: int        # not in Kaggle dataset, set to 0
    rating: Optional[str] = None
    vote_count: int = 0
    original_language: str = "en"
    production_countries: str = ""
    rank: int = 0
    foreign_gross: int = 0
    domestic_pct: float = 0.0
    foreign_pct: float = 0.0

    @property
    def multiplier(self) -> Optional[float]:
        """Revenue / budget multiplier."""
        if self.budget > 0 and self.worldwide_gross > 0:
            return round(self.worldwide_gross / self.budget, 2)
        return None

    @property
    def primary_genre(self) -> str:
        return self.genres[0] if self.genres else "Unknown"

    @property
    def rating_value(self) -> Optional[float]:
        """Extract numeric rating from string like '7.8/10'."""
        if self.rating:
            try:
                return float(self.rating.split("/")[0])
            except (ValueError, IndexError):
                pass
        return None


# ─────────────────────────────────────────────────
# In-memory dataset (loaded once at import)
# ─────────────────────────────────────────────────

_DATASET: List[BoxOfficeRecord] = []


def _safe_float(val) -> float:
    """Safely parse a float, returning 0.0 on failure."""
    try:
        return float(val) if val else 0.0
    except (ValueError, TypeError):
        return 0.0


def _safe_int(val) -> int:
    """Safely parse an int from a float string, returning 0 on failure."""
    try:
        return int(float(val)) if val else 0
    except (ValueError, TypeError):
        return 0


# NOTE: Kaggle dataset has NO budget column.
# Budget = 0 here; real budget comes from TMDb API in service.py.


def _load_dataset() -> List[BoxOfficeRecord]:
    """Load the real Kaggle CSV into memory."""
    records: List[BoxOfficeRecord] = []
    if not os.path.exists(_CSV_PATH):
        return records
    with open(_CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                title = row.get("Release Group", "").strip()
                if not title:
                    continue

                worldwide = _safe_int(row.get("$Worldwide", 0))
                domestic = _safe_int(row.get("$Domestic", 0))
                foreign = _safe_int(row.get("$Foreign", 0))
                year = _safe_int(row.get("Year", 2000))
                genres_str = row.get("Genres", "")
                genres = [g.strip() for g in genres_str.split(",") if g.strip()]
                rating = row.get("Rating", "")
                vote_count = _safe_int(row.get("Vote_Count", 0))
                dom_pct = _safe_float(row.get("Domestic %", 0))
                for_pct = _safe_float(row.get("Foreign %", 0))
                rank = _safe_int(row.get("Rank", 0))
                lang = row.get("Original_Language", "en") or "en"
                countries = row.get("Production_Countries", "") or ""

                records.append(BoxOfficeRecord(
                    title=title,
                    year=year,
                    genres=genres,
                    budget=0,  # no budget in Kaggle; TMDb provides real budget
                    worldwide_gross=worldwide,
                    domestic_gross=domestic,
                    opening_weekend=0,
                    rating=rating if rating else None,
                    vote_count=vote_count,
                    original_language=lang,
                    production_countries=countries,
                    rank=rank,
                    foreign_gross=foreign,
                    domestic_pct=dom_pct,
                    foreign_pct=for_pct,
                ))
            except (ValueError, KeyError):
                continue
    return records


# Load once at module import
_DATASET = _load_dataset()


def dataset_size() -> int:
    """Return number of records loaded."""
    return len(_DATASET)


# ─────────────────────────────────────────────────
# Title normalization for fuzzy matching
# ─────────────────────────────────────────────────

def _normalize(title: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    s = title.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _title_match_score(query: str, record_title: str) -> float:
    """
    Return a 0.0-1.0 match score between query and record title.
    """
    nq = _normalize(query)
    nt = _normalize(record_title)

    if nq == nt:
        return 1.0

    # Substring match — require shorter >= 50% of longer to avoid
    # false positives like "ali" matching "bahubali"
    if nq in nt or nt in nq:
        shorter = min(len(nq), len(nt))
        longer = max(len(nq), len(nt))
        ratio = shorter / longer if longer > 0 else 0
        if ratio >= 0.50:
            return 0.6 + 0.3 * ratio
        # Fall through to word-overlap if ratio too low

    q_words = set(nq.split())
    t_words = set(nt.split())
    if not q_words:
        return 0.0
    overlap = len(q_words & t_words)
    return 0.5 * (overlap / max(len(q_words), len(t_words)))


# ─────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────

def lookup_movie(title: str) -> Optional[BoxOfficeRecord]:
    """
    Find best matching movie in the dataset.
    Returns None if no match scores above 0.5.
    """
    if not _DATASET:
        return None

    best_record: Optional[BoxOfficeRecord] = None
    best_score = 0.0

    for rec in _DATASET:
        score = _title_match_score(title, rec.title)
        if score > best_score:
            best_score = score
            best_record = rec

    return best_record if best_score >= 0.65 else None


def all_titles() -> List[str]:
    """Return all movie titles in the dataset (sorted)."""
    return sorted(set(r.title for r in _DATASET))


def find_comparables(
    genres: List[str],
    budget: int,
    year: int,
    exclude_title: Optional[str] = None,
    budget_tolerance: float = 0.30,
    year_tolerance: int = 5,
    max_results: int = 8,
) -> List[BoxOfficeRecord]:
    """
    Find comparable films from Kaggle dataset.
    Filters: genre match, budget band, year range, outlier trimming.
    """
    if not _DATASET or budget <= 0:
        return []

    genre_set = set(g.strip().lower() for g in genres[:3])
    budget_lo = int(budget * (1 - budget_tolerance))
    budget_hi = int(budget * (1 + budget_tolerance))
    year_lo = year - year_tolerance
    year_hi = year + year_tolerance
    exclude_norm = _normalize(exclude_title) if exclude_title else ""

    candidates: List[BoxOfficeRecord] = []
    for rec in _DATASET:
        if exclude_norm and _normalize(rec.title) == exclude_norm:
            continue
        rec_genres = set(g.lower() for g in rec.genres[:3])
        if not genre_set & rec_genres:
            continue
        if rec.budget < budget_lo or rec.budget > budget_hi:
            continue
        if rec.year < year_lo or rec.year > year_hi:
            continue
        if rec.worldwide_gross <= 0:
            continue
        candidates.append(rec)

    # Trim outliers (top & bottom 5%)
    if len(candidates) > 4:
        candidates.sort(key=lambda r: r.multiplier or 0)
        trim = max(1, len(candidates) // 20)
        if len(candidates) > 2 * trim:
            candidates = candidates[trim:-trim]

    candidates.sort(key=lambda r: r.worldwide_gross, reverse=True)
    return candidates[:max_results]


def find_comparables_relaxed(
    genres: List[str],
    budget: int,
    year: int,
    exclude_title: Optional[str] = None,
    max_results: int = 8,
) -> List[BoxOfficeRecord]:
    """Try strict first, then widen criteria progressively."""
    results = find_comparables(genres, budget, year, exclude_title, 0.30, 5, max_results)
    if len(results) >= 3:
        return results
    results = find_comparables(genres, budget, year, exclude_title, 0.60, 5, max_results)
    if len(results) >= 3:
        return results
    results = find_comparables(genres, budget, year, exclude_title, 0.60, 10, max_results)
    if len(results) >= 3:
        return results
    return find_comparables(genres, budget, year, exclude_title, 1.0, 15, max_results)


def get_genre_stats(genres: List[str]) -> dict:
    """Get statistical summaries for the given genres from the dataset."""
    genre_set = set(g.strip().lower() for g in genres[:3])

    genre_films: List[BoxOfficeRecord] = []
    for rec in _DATASET:
        rec_genres = set(g.lower() for g in rec.genres[:3])
        if genre_set & rec_genres and rec.worldwide_gross > 0 and rec.budget > 0:
            genre_films.append(rec)

    if not genre_films:
        return {
            "count": 0,
            "avg_multiplier": 3.0,
            "median_multiplier": 2.5,
            "avg_revenue": 100_000_000,
            "p25_multiplier": 1.5,
            "p75_multiplier": 5.0,
            "top_films": [],
        }

    multipliers = sorted([r.multiplier for r in genre_films if r.multiplier])
    revenues = [r.worldwide_gross for r in genre_films]

    def percentile(sorted_list: list, p: float):
        if not sorted_list:
            return 0
        idx = min(int(len(sorted_list) * p), len(sorted_list) - 1)
        return sorted_list[idx]

    top_films = sorted(genre_films, key=lambda r: r.worldwide_gross, reverse=True)[:5]

    return {
        "count": len(genre_films),
        "avg_multiplier": round(sum(multipliers) / len(multipliers), 2) if multipliers else 3.0,
        "median_multiplier": round(percentile(multipliers, 0.5), 2),
        "avg_revenue": int(sum(revenues) / len(revenues)),
        "p25_multiplier": round(percentile(multipliers, 0.25), 2),
        "p75_multiplier": round(percentile(multipliers, 0.75), 2),
        "top_films": [{"title": r.title, "year": r.year, "multiplier": r.multiplier} for r in top_films],
    }


# ─────────────────────────────────────────────────
# Percentile engine & performance classification
# ─────────────────────────────────────────────────

def _percentile_rank(value: float, sorted_values: list) -> int:
    """Return the percentile rank (0-100) of value within sorted_values."""
    if not sorted_values:
        return 50
    count_below = sum(1 for v in sorted_values if v < value)
    return int((count_below / len(sorted_values)) * 100)


def classify_performance(percentile: int) -> str:
    """Top 20% → High Performer, 40-60% → Average, Bottom 20% → Underperformer."""
    if percentile >= 80:
        return "High Performer"
    elif percentile >= 40:
        return "Average Performer"
    else:
        return "Underperformer"


def compute_movie_percentiles(rec: BoxOfficeRecord) -> dict:
    """
    Compute dynamic percentile positions across the entire 5000-film dataset.
    """
    genre_set = set(g.lower() for g in rec.genres[:3])

    # Revenue percentile within genre
    genre_revenues = sorted([
        r.worldwide_gross for r in _DATASET
        if set(g.lower() for g in r.genres[:3]) & genre_set
        and r.worldwide_gross > 0
    ])
    revenue_pct = _percentile_rank(rec.worldwide_gross, genre_revenues)

    # Budget percentile within year (+/-2)
    year_budgets = sorted([
        r.budget for r in _DATASET
        if abs(r.year - rec.year) <= 2 and r.budget > 0
    ])
    budget_pct = _percentile_rank(rec.budget, year_budgets)

    # Multiplier percentile across entire dataset
    all_mults = sorted([
        r.multiplier for r in _DATASET
        if r.multiplier is not None and r.multiplier > 0
    ])
    mult_pct = _percentile_rank(float(rec.multiplier or 0), all_mults)

    return {
        "revenue_percentile_in_genre": revenue_pct,
        "budget_percentile_in_year": budget_pct,
        "multiplier_percentile_overall": mult_pct,
        "revenue_classification": classify_performance(revenue_pct),
        "multiplier_classification": classify_performance(mult_pct),
        "genre_peer_count": len(genre_revenues),
        "year_peer_count": len(year_budgets),
        "dataset_total": len(all_mults),
    }
