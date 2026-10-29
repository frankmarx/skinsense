from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey, ForeignKeyConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from chalicelib.db import Base

class ItemDayListing(Base):
    __tablename__ = 'item_day_listing'

    item_id = Column(String, primary_key=True)
    datasource_id = Column(String, primary_key=True)
    day = Column(Date, primary_key=True)
    
    listings_count = Column(Integer, default=0)
    min_price = Column(Float)
    ins_job_id = Column(UUID(as_uuid=True), nullable=False)
    upd_job_id = Column(UUID(as_uuid=True), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['item_id'],
            ['skinsense.item_master.item_id'],
        ),
        ForeignKeyConstraint(
            ['datasource_id'],
            ['skinsense.datasource.datasource_id'],
        ),
        {'schema': 'skinsense'},
    )

    item = relationship("ItemMaster", back_populates="day_listings")
    datasource = relationship("Datasource", back_populates="day_listings")
