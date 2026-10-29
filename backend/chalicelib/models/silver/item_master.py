from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from chalicelib.db import Base

class ItemMaster(Base):
    __tablename__ = 'item_master'
    __table_args__ = {'schema': 'skinsense'}

    item_id = Column(String, primary_key=True)
    
    full_name = Column(String, nullable=False)
    item_type = Column(String)
    wear = Column(String)
    stat_track = Column(Boolean)
    ins_job_id = Column(UUID(as_uuid=True), nullable=False)
    upd_job_id = Column(UUID(as_uuid=True), nullable=False)

    # Relationships
    day_sales = relationship("ItemDaySales", back_populates="item")
    day_listings = relationship("ItemDayListing", back_populates="item")
    listing_details = relationship("ItemListingDetail", back_populates="item")
