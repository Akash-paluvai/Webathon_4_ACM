"""
Phase 8 configuration — API keys loaded from environment variables.
Keys are never logged, printed, or exposed in responses.
"""

import os

TMDB_API_KEY: str = os.environ.get("TMDB_API_KEY", "")
OMDB_API_KEY: str = os.environ.get("OMDB_API_KEY", "")
YOUTUBE_API_KEY: str = os.environ.get("YOUTUBE_API_KEY", "")

# Reddit API (OAuth2 script app)
REDDIT_CLIENT_ID: str = os.environ.get("REDDIT_CLIENT_ID", "goxEQaAH8pzNbqIC7eYfyA")
REDDIT_CLIENT_SECRET: str = os.environ.get("REDDIT_CLIENT_SECRET", "kuRIr1BZw9-3vCAXtnmaL1uapiuG6Q")
REDDIT_USER_AGENT: str = "FilmFlowPhase8/1.0"

TMDB_BASE_URL = "https://api.themoviedb.org/3"
OMDB_BASE_URL = "https://www.omdbapi.com"
YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"
REDDIT_TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
REDDIT_SEARCH_URL = "https://oauth.reddit.com/search"

# Timeouts and cache TTLs
REQUEST_TIMEOUT_SECONDS = 10
CACHE_TTL_SECONDS = 6 * 60 * 60  # 6 hours

