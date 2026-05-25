from sqlalchemy import Column, String, Float, DateTime, func
from chalicelib.db import Base

class Price(Base):
    __tablename__ = 'prices'

    market_hash_name = Column(String, primary_key=True)
    price = Column(Float, nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
