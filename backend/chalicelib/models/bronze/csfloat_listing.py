from sqlalchemy import Column, String, Integer
from chalicelib.db import Base

class CSFloatListing(Base):
    __tablename__ = 'csfloat_listing'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String)
    
    market_hash_name = Column(String)
    quantity = Column(Integer)
    min_price = Column(Integer)
