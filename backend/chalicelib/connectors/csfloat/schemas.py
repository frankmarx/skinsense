from pydantic import BaseModel, Json
from typing import Dict, Any, List

# --- Simplified Listing Model ---
class Listing(BaseModel):
    """Represents a simplified item listing summary."""
    market_hash_name: str
    price: float
    quantity: int

# --- Simplified Listing Detail Model using JSON ---
class ListingDetail(BaseModel):
    """The full entity returned from CSFloat for a specific listing."""
    id: str
    created_at: str # Consider keeping as str or using Pydantic's datetime handling
    type: str
    price: float
    state: str
    seller: Json[Dict[str, Any]]
    item: Json[Dict[str, Any]]
    is_seller: bool
    min_offer_price: float
    max_offer_discount: float
    is_watchlisted: bool
    watchers: int
