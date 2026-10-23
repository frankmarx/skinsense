from sqlalchemy import Column, String, Float, Integer, BigInteger, Index
from chalicelib.db import Base

class SkinportItem(Base):
    __tablename__ = 'skinport_item'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False)

    market_hash_name = Column(String, nullable=False)
    currency = Column(String, nullable=False)
    suggested_price = Column(Float, nullable=True)
    item_page = Column(String, nullable=True)
    market_page = Column(String, nullable=True)
    min_price = Column(Float, nullable=True)
    max_price = Column(Float, nullable=True)
    mean_price = Column(Float, nullable=True)
    median_price = Column(Float, nullable=True)
    quantity = Column(Integer, nullable=True)
    created_at = Column(BigInteger, nullable=True)
    updated_at = Column(BigInteger, nullable=True)

    __table_args__ = (
        Index('idx_skinport_item_job_id', 'job_id'),
        {'schema': 'skinsense'},
    )
