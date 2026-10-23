"""
Pydantic models for CSFloat API responses.

CSFloat removed their developer docs; the last archived copy is at:
https://web.archive.org/web/20260320124433/https://docs.csfloat.com/

All endpoints are relative to the base URL https://csfloat.com/api/v1
(see CSFLOAT_BASE_URL in client.py). Each model below is annotated with
the endpoint(s) that return it. When adding a new endpoint, add its
models under a matching section header.
"""
from pydantic import BaseModel
from typing import Any, Dict, List, Optional


# ===========================================================================
# GET /listings/price-list
# Global price list: one summary entry per market_hash_name.
# Public endpoint (no auth required).
# ===========================================================================
class Listing(BaseModel):
    """A simplified item listing summary from the price-list endpoint."""
    market_hash_name: str
    min_price: float
    quantity: int


# ===========================================================================
# GET /listings (with query params, e.g. market_hash_name, limit, cursor)
# Paginated listing search; envelope is {"data": [ListingDetail, ...], "cursor": "..."}.
# GET /listings/<ID> returns a single object of the same shape.
# Auth required. Fields marked Optional are not present on every listing
# (e.g. auction_details only appears on auction-type listings).
# ===========================================================================
class ListingDetail(BaseModel):
    """The full entity returned from CSFloat for a specific listing."""
    id: str
    created_at: str # Consider keeping as str or using Pydantic's datetime handling
    type: str
    price: float
    state: str
    seller: Dict[str, Any]
    item: Dict[str, Any]
    is_seller: bool
    is_watchlisted: bool
    watchers: int
    reference: Optional[Dict[str, Any]] = None
    auction_details: Optional[Dict[str, Any]] = None
    min_offer_price: Optional[float] = None
    max_offer_discount: Optional[float] = None
