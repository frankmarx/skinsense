from pydantic import BaseModel

class CSFloatListing(BaseModel):
    market_hash_name: str
    quantity: int
    min_price: int
