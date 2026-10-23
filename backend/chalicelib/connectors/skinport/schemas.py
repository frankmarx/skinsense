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


class Item(BaseModel):
    """A single item's market data from SkinPort /v1/items."""
    market_hash_name: str
    version: Optional[str] = None
    currency: str
    suggested_price: Optional[float] = None
    item_page: Optional[str] = None
    market_page: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    mean_price: Optional[float] = None
    median_price: Optional[float] = None
    quantity: int = 0
    created_at: Optional[int] = None
    updated_at: Optional[int] = None
