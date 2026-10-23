from sqlalchemy import Column, String, Float, Integer, Index
from chalicelib.db import Base

class SkinportSalesHistory(Base):
    __tablename__ = 'skinport_sales_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False)

    market_hash_name = Column(String, nullable=False)
    version = Column(String, nullable=True)
    currency = Column(String, nullable=False)
    item_page = Column(String, nullable=True)
    market_page = Column(String, nullable=True)

    last_24_hours_min = Column(Float, nullable=True)
    last_24_hours_max = Column(Float, nullable=True)
    last_24_hours_avg = Column(Float, nullable=True)
    last_24_hours_median = Column(Float, nullable=True)
    last_24_hours_volume = Column(Integer, nullable=True)

    last_7_days_min = Column(Float, nullable=True)
    last_7_days_max = Column(Float, nullable=True)
    last_7_days_avg = Column(Float, nullable=True)
    last_7_days_median = Column(Float, nullable=True)
    last_7_days_volume = Column(Integer, nullable=True)

    last_30_days_min = Column(Float, nullable=True)
    last_30_days_max = Column(Float, nullable=True)
    last_30_days_avg = Column(Float, nullable=True)
    last_30_days_median = Column(Float, nullable=True)
    last_30_days_volume = Column(Integer, nullable=True)

    last_90_days_min = Column(Float, nullable=True)
    last_90_days_max = Column(Float, nullable=True)
    last_90_days_avg = Column(Float, nullable=True)
    last_90_days_median = Column(Float, nullable=True)
    last_90_days_volume = Column(Integer, nullable=True)

    __table_args__ = (
        Index('idx_skinport_sales_history_job_id', 'job_id'),
        {'schema': 'skinsense'},
    )
