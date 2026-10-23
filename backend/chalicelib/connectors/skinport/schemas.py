from pydantic import BaseModel
from typing import Optional


class SalesPeriodStats(BaseModel):
    """Aggregated sale statistics for a single time period."""
    min: Optional[float] = None
    max: Optional[float] = None
    avg: Optional[float] = None
    median: Optional[float] = None
    volume: int = 0


class SalesHistoryEntry(BaseModel):
    """A single item's sales history from SkinPort /v1/sales/history."""
    market_hash_name: str
    version: Optional[str] = None
    currency: str
    item_page: Optional[str] = None
    market_page: Optional[str] = None
    last_24_hours: SalesPeriodStats
    last_7_days: SalesPeriodStats
    last_30_days: SalesPeriodStats
    last_90_days: SalesPeriodStats
