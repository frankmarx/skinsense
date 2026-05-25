from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# --- Simplified Listing Model ---
class Listing(BaseModel):
    """Represents a simplified item listing summary."""
    market_hash_name: str
    price: float
    quantity: int

# --- Detailed Listing Models ---

class SCMInfo(BaseModel):
    """Steam Community Market data."""
    price: Optional[float] = None
    volume: Optional[int] = None

class StickerInfo(BaseModel):
    """Sticker details on a specific item."""
    stickerId: int
    slot: int
    icon_url: str
    name: str
    scm: Optional[SCMInfo] = None

class ItemInfo(BaseModel):
    """Detailed item attributes."""
    asset_id: str
    def_index: int
    paint_index: int
    paint_seed: int
    float_value: float
    icon_url: str
    d_param: str
    is_stattrak: bool
    is_souvenir: bool
    rarity: int
    quality: int
    market_hash_name: str
    stickers: List[StickerInfo] = []
    tradable: int
    inspect_link: str
    has_screenshot: bool
    scm: Optional[SCMInfo] = None
    item_name: str
    wear_name: str
    description: Optional[str] = None
    collection: Optional[str] = None
    badges: List[str] = []

class SellerStatistics(BaseModel):
    """Seller's trade performance stats."""
    median_trade_time: int
    total_failed_trades: int
    total_trades: int
    total_verified_trades: int

class SellerInfo(BaseModel):
    """Detailed information about the listing seller."""
    avatar: str
    flags: int
    online: bool
    stall_public: bool
    statistics: SellerStatistics
    steam_id: str
    username: str

class ListingDetail(BaseModel):
    """The full entity returned from CSFloat for a specific listing."""
    id: str
    created_at: datetime
    type: str
    price: float
    state: str
    seller: SellerInfo
    item: ItemInfo
    is_seller: bool
    min_offer_price: float
    max_offer_discount: float
    is_watchlisted: bool
    watchers: int
