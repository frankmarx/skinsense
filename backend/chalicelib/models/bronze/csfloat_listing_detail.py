from sqlalchemy import Column, String, Integer, JSON, Boolean
from chalicelib.db import Base

class CSFloatListingDetail(Base):
    __tablename__ = 'csfloat_listing_detail'
    __table_args__ = {'schema': 'skinsense'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String)

    listing_id = Column(String)
    created_at = Column(String)
    type = Column(String)
    price = Column(Integer)
    state = Column(String)
    is_seller = Column(Boolean)
    is_watchlisted = Column(Boolean)
    watchers = Column(Integer)

    seller = Column(JSON)
    item = Column(JSON)
    reference = Column(JSON)
    auction_details = Column(JSON)
