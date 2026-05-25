from pydantic import BaseModel
from typing import List

class Statistics(BaseModel):
    median_trade_time: int
    total_failed_trades: int
    total_trades: int
    total_verified_trades: int

class Seller(BaseModel):
    avatar: str
    flags: int
    online: bool
    stall_public: bool
    statistics: Statistics
    steam_id: str
    username: str

class SCM(BaseModel):
    price: int
    volume: int

class Sticker(BaseModel):
    stickerId: int
    slot: int
    icon_url: str
    name: str
    scm: SCM

class Item(BaseModel):
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
    stickers: List[Sticker]
    tradable: int
    inspect_link: str
    has_screenshot: bool
    scm: SCM
    item_name: str
    wear_name: str
    description: str
    collection: str
    badges: List[str]

class CSFloatListingDetail(BaseModel):
    id: str
    created_at: str
    type: str
    price: int
    state: str
    seller: Seller
    item: Item
    is_seller: bool
    min_offer_price: int
    max_offer_discount: int
    is_watchlisted: bool
    watchers: int
