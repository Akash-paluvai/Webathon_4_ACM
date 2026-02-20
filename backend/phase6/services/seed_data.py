"""
Seed Data — populates HistoricalFilm, DealBenchmark, CompetitionRelease tables
with realistic synthetic data.  Idempotent (skips if rows already exist).
"""

from sqlalchemy.orm import Session
from phase6_models import HistoricalFilm, DealBenchmark, CompetitionRelease


def seed_historical_films(db: Session) -> None:
    if db.query(HistoricalFilm).first():
        return

    films = [
        # Hollywood blockbusters
        HistoricalFilm(title="Galactic Storm", genre="Action", language="English", cast_tier="starDriven",
            budget_usd=200, budget_level="high", revenue_usd=850, roi=3.25, release_mode="theatre",
            ott_revenue_pct=25, theatre_revenue_pct=75,
            region_north_america_pct=40, region_europe_pct=25, region_east_asia_pct=18,
            region_south_asia_pct=5, region_latin_america_pct=7, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=18, year=2025),
        HistoricalFilm(title="The Last Frontier", genre="Sci-Fi", language="English", cast_tier="established",
            budget_usd=150, budget_level="high", revenue_usd=520, roi=2.47, release_mode="theatre",
            ott_revenue_pct=30, theatre_revenue_pct=70,
            region_north_america_pct=38, region_europe_pct=28, region_east_asia_pct=15,
            region_south_asia_pct=6, region_latin_america_pct=8, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=15, year=2024),
        HistoricalFilm(title="Nightmare Lane", genre="Horror", language="English", cast_tier="emerging",
            budget_usd=12, budget_level="low", revenue_usd=180, roi=14.0, release_mode="theatre",
            ott_revenue_pct=40, theatre_revenue_pct=60,
            region_north_america_pct=50, region_europe_pct=22, region_east_asia_pct=10,
            region_south_asia_pct=5, region_latin_america_pct=8, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=0, dubbed_revenue_uplift_pct=0, year=2025),
        # OTT releases
        HistoricalFilm(title="Silent Witness", genre="Thriller", language="English", cast_tier="established",
            budget_usd=60, budget_level="medium", revenue_usd=0, roi=0, release_mode="ott",
            ott_revenue_pct=100, theatre_revenue_pct=0,
            region_north_america_pct=35, region_europe_pct=30, region_east_asia_pct=12,
            region_south_asia_pct=8, region_latin_america_pct=10, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=22, year=2025),
        HistoricalFilm(title="Love in Milan", genre="Romance", language="English", cast_tier="emerging",
            budget_usd=25, budget_level="medium", revenue_usd=0, roi=0, release_mode="ott",
            ott_revenue_pct=100, theatre_revenue_pct=0,
            region_north_america_pct=30, region_europe_pct=35, region_east_asia_pct=8,
            region_south_asia_pct=12, region_latin_america_pct=10, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=12, year=2024),
        # Indian films
        HistoricalFilm(title="Bahubali Returns", genre="Action", language="Hindi", cast_tier="starDriven",
            budget_usd=45, budget_level="high", revenue_usd=320, roi=6.11, release_mode="theatre",
            ott_revenue_pct=35, theatre_revenue_pct=65,
            region_north_america_pct=8, region_europe_pct=5, region_east_asia_pct=3,
            region_south_asia_pct=72, region_latin_america_pct=2, region_middle_east_pct=8, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=35, year=2025),
        HistoricalFilm(title="Mumbai Diaries", genre="Drama", language="Hindi", cast_tier="established",
            budget_usd=8, budget_level="low", revenue_usd=0, roi=0, release_mode="ott",
            ott_revenue_pct=100, theatre_revenue_pct=0,
            region_north_america_pct=10, region_europe_pct=5, region_east_asia_pct=2,
            region_south_asia_pct=70, region_latin_america_pct=2, region_middle_east_pct=9, region_africa_pct=2,
            was_dubbed=0, dubbed_revenue_uplift_pct=0, year=2024),
        HistoricalFilm(title="RRR Legacy", genre="Action", language="Telugu", cast_tier="starDriven",
            budget_usd=55, budget_level="high", revenue_usd=260, roi=3.73, release_mode="theatre",
            ott_revenue_pct=40, theatre_revenue_pct=60,
            region_north_america_pct=12, region_europe_pct=5, region_east_asia_pct=8,
            region_south_asia_pct=60, region_latin_america_pct=3, region_middle_east_pct=10, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=40, year=2025),
        # Korean films
        HistoricalFilm(title="Parasite Rebirth", genre="Thriller", language="Korean", cast_tier="established",
            budget_usd=20, budget_level="medium", revenue_usd=380, roi=18.0, release_mode="theatre",
            ott_revenue_pct=45, theatre_revenue_pct=55,
            region_north_america_pct=25, region_europe_pct=20, region_east_asia_pct=40,
            region_south_asia_pct=5, region_latin_america_pct=5, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=28, year=2024),
        # Festival / Indie
        HistoricalFilm(title="Moonlit Roads", genre="Drama", language="English", cast_tier="unknown",
            budget_usd=2, budget_level="low", revenue_usd=8, roi=3.0, release_mode="hybrid",
            ott_revenue_pct=70, theatre_revenue_pct=30,
            region_north_america_pct=40, region_europe_pct=35, region_east_asia_pct=5,
            region_south_asia_pct=5, region_latin_america_pct=8, region_middle_east_pct=4, region_africa_pct=3,
            was_dubbed=0, dubbed_revenue_uplift_pct=0, year=2025),
        HistoricalFilm(title="Desert Blues", genre="Documentary", language="English", cast_tier="unknown",
            budget_usd=1.5, budget_level="low", revenue_usd=5, roi=2.33, release_mode="hybrid",
            ott_revenue_pct=80, theatre_revenue_pct=20,
            region_north_america_pct=35, region_europe_pct=40, region_east_asia_pct=5,
            region_south_asia_pct=5, region_latin_america_pct=5, region_middle_east_pct=7, region_africa_pct=3,
            was_dubbed=0, dubbed_revenue_uplift_pct=0, year=2024),
        HistoricalFilm(title="Laugh Factory", genre="Comedy", language="English", cast_tier="starDriven",
            budget_usd=80, budget_level="high", revenue_usd=350, roi=3.38, release_mode="theatre",
            ott_revenue_pct=35, theatre_revenue_pct=65,
            region_north_america_pct=45, region_europe_pct=22, region_east_asia_pct=10,
            region_south_asia_pct=8, region_latin_america_pct=10, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=10, year=2025),
        HistoricalFilm(title="Cosmic Dreamers", genre="Animation", language="English", cast_tier="established",
            budget_usd=120, budget_level="high", revenue_usd=600, roi=4.0, release_mode="theatre",
            ott_revenue_pct=30, theatre_revenue_pct=70,
            region_north_america_pct=35, region_europe_pct=25, region_east_asia_pct=20,
            region_south_asia_pct=5, region_latin_america_pct=10, region_middle_east_pct=3, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=25, year=2024),
        HistoricalFilm(title="Spanish Sun", genre="Romance", language="Spanish", cast_tier="emerging",
            budget_usd=10, budget_level="low", revenue_usd=55, roi=4.5, release_mode="hybrid",
            ott_revenue_pct=60, theatre_revenue_pct=40,
            region_north_america_pct=15, region_europe_pct=20, region_east_asia_pct=2,
            region_south_asia_pct=2, region_latin_america_pct=55, region_middle_east_pct=3, region_africa_pct=3,
            was_dubbed=1, dubbed_revenue_uplift_pct=15, year=2025),
        HistoricalFilm(title="K-Drama: The Movie", genre="Romance", language="Korean", cast_tier="starDriven",
            budget_usd=30, budget_level="medium", revenue_usd=250, roi=7.33, release_mode="hybrid",
            ott_revenue_pct=55, theatre_revenue_pct=45,
            region_north_america_pct=18, region_europe_pct=15, region_east_asia_pct=45,
            region_south_asia_pct=8, region_latin_america_pct=8, region_middle_east_pct=4, region_africa_pct=2,
            was_dubbed=1, dubbed_revenue_uplift_pct=20, year=2024),
    ]
    db.add_all(films)
    db.commit()


def seed_deal_benchmarks(db: Session) -> None:
    if db.query(DealBenchmark).first():
        return

    # platform_name, genre, avg_advance_pct, avg_rev_share, min_guarantee_usd_k, exclusive_window_days, sample_count
    rows = [
        ("Netflix", "Action", 15, 20, 200, 365, 45),
        ("Netflix", "Drama", 12, 22, 150, 365, 60),
        ("Netflix", "Thriller", 14, 21, 180, 330, 38),
        ("Netflix", "Comedy", 10, 23, 120, 300, 50),
        ("Netflix", "Horror", 18, 19, 80, 270, 30),
        ("Netflix", "Romance", 8, 24, 100, 300, 35),
        ("Netflix", "Sci-Fi", 16, 20, 250, 365, 25),
        ("Netflix", "Documentary", 6, 28, 50, 365, 40),
        ("Netflix", "Animation", 12, 22, 200, 365, 20),
        ("Amazon Prime", "Action", 12, 22, 150, 270, 35),
        ("Amazon Prime", "Drama", 10, 24, 120, 270, 50),
        ("Amazon Prime", "Thriller", 11, 23, 130, 240, 30),
        ("Amazon Prime", "Comedy", 9, 25, 100, 240, 40),
        ("Amazon Prime", "Horror", 14, 21, 60, 210, 22),
        ("Amazon Prime", "Romance", 7, 26, 80, 240, 28),
        ("Amazon Prime", "Sci-Fi", 13, 22, 180, 300, 18),
        ("Amazon Prime", "Documentary", 5, 30, 40, 300, 35),
        ("Amazon Prime", "Animation", 10, 24, 150, 300, 15),
        ("Theatrical", "Action", 20, 45, 300, 180, 60),
        ("Theatrical", "Drama", 10, 50, 100, 150, 45),
        ("Theatrical", "Thriller", 15, 48, 200, 150, 35),
        ("Theatrical", "Comedy", 12, 47, 150, 120, 55),
        ("Theatrical", "Horror", 25, 42, 50, 120, 40),
        ("Theatrical", "Sci-Fi", 18, 45, 350, 180, 30),
        ("Theatrical", "Animation", 15, 43, 250, 180, 25),
        ("Hotstar", "Action", 10, 18, 80, 300, 25),
        ("Hotstar", "Drama", 8, 20, 60, 300, 40),
        ("Hotstar", "Thriller", 9, 19, 70, 270, 20),
        ("Hotstar", "Comedy", 7, 22, 50, 270, 30),
        ("Hotstar", "Romance", 6, 23, 40, 240, 25),
        ("Festival Circuit", "Drama", 3, 35, 10, 90, 80),
        ("Festival Circuit", "Documentary", 2, 40, 5, 90, 60),
        ("Festival Circuit", "Thriller", 4, 33, 15, 90, 30),
        ("YouTube Premium", "Comedy", 5, 30, 30, 180, 25),
        ("YouTube Premium", "Horror", 8, 28, 25, 180, 18),
        ("YouTube Premium", "Documentary", 3, 35, 15, 210, 30),
        ("YouTube Premium", "Drama", 5, 32, 25, 210, 20),
    ]

    benchmarks = [
        DealBenchmark(
            platform_name=r[0], genre=r[1], avg_advance_pct=r[2], avg_rev_share=r[3],
            min_guarantee_usd_k=r[4], exclusive_window_days=r[5], sample_count=r[6]
        )
        for r in rows
    ]
    db.add_all(benchmarks)
    db.commit()


def seed_competition_releases(db: Session) -> None:
    if db.query(CompetitionRelease).first():
        return

    releases = [
        CompetitionRelease(title="Thunder Strike", genre="Action", language="English", budget_level="high", release_mode="theatre", release_quarter="2026-Q1", star_power=0.9),
        CompetitionRelease(title="Shadow Protocol", genre="Thriller", language="English", budget_level="high", release_mode="theatre", release_quarter="2026-Q1", star_power=0.8),
        CompetitionRelease(title="Love Actually 2", genre="Romance", language="English", budget_level="medium", release_mode="hybrid", release_quarter="2026-Q1", star_power=0.7),
        CompetitionRelease(title="The Verdict", genre="Drama", language="English", budget_level="medium", release_mode="ott", release_quarter="2026-Q1", star_power=0.6),
        CompetitionRelease(title="K-Wave", genre="Action", language="Korean", budget_level="high", release_mode="theatre", release_quarter="2026-Q1", star_power=0.85),
        CompetitionRelease(title="Pushpa 3", genre="Action", language="Telugu", budget_level="high", release_mode="theatre", release_quarter="2026-Q1", star_power=0.95),
        CompetitionRelease(title="Laugh Riot", genre="Comedy", language="English", budget_level="medium", release_mode="ott", release_quarter="2026-Q1", star_power=0.5),
        CompetitionRelease(title="Dark Hollow", genre="Horror", language="English", budget_level="low", release_mode="theatre", release_quarter="2026-Q2", star_power=0.3),
        CompetitionRelease(title="Ocean Planet", genre="Sci-Fi", language="English", budget_level="high", release_mode="theatre", release_quarter="2026-Q2", star_power=0.85),
        CompetitionRelease(title="Dil Se 2", genre="Romance", language="Hindi", budget_level="medium", release_mode="hybrid", release_quarter="2026-Q2", star_power=0.7),
        CompetitionRelease(title="Jawan 2", genre="Action", language="Hindi", budget_level="high", release_mode="theatre", release_quarter="2026-Q2", star_power=0.95),
        CompetitionRelease(title="The Documentary", genre="Documentary", language="English", budget_level="low", release_mode="hybrid", release_quarter="2026-Q2", star_power=0.2),
    ]
    db.add_all(releases)
    db.commit()


def seed_all(db: Session) -> None:
    """Seed all Phase 6 reference data."""
    seed_historical_films(db)
    seed_deal_benchmarks(db)
    seed_competition_releases(db)
