"""
Abstract base class for Phase 8 data-source adapters.
Each adapter wraps one external API and returns DataSourceResult objects.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Any, Optional

from phase8.schemas import DataSourceResult


class BaseAdapter(ABC):
    """Interface every Phase 8 data adapter must implement."""

    source_name: str = "unknown"

    @abstractmethod
    async def is_available(self) -> bool:
        """Return True if the adapter has a valid API key and can make requests."""
        ...

    def _ok(
        self,
        value: Any,
        confidence: float = 0.95,
        methodology: Optional[str] = None,
    ) -> DataSourceResult:
        """Helper to build a successful live-data result."""
        return DataSourceResult(
            value=value,
            source_type="actual",
            source_name=self.source_name,
            confidence=confidence,
            methodology=methodology,
        )

    def _estimated(
        self,
        value: Any,
        confidence: float,
        methodology: str,
    ) -> DataSourceResult:
        """Helper to build an estimation result."""
        return DataSourceResult(
            value=value,
            source_type="estimated",
            source_name="estimation_engine",
            confidence=confidence,
            methodology=methodology,
        )

    def _fallback(
        self,
        value: Any,
        confidence: float = 0.40,
        methodology: Optional[str] = None,
    ) -> DataSourceResult:
        """Helper to build a fallback result."""
        return DataSourceResult(
            value=value,
            source_type="fallback",
            source_name=self.source_name,
            confidence=confidence,
            methodology=methodology,
        )
