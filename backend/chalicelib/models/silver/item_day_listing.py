from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey
from sqlalchemy.orm import relationship
from chalicelib.db import Base

class ItemDayListing(Base):
    __tablename__ = 'item_day_listing'

    item_id = Column(String, ForeignKey('item_master.item_id'), primary_key=True)
    datasource_id = Column(String, ForeignKey('datasource.datasource_id'), primary_key=True)
    day = Column(Date, primary_key=True)
    
    listings_count = Column(Integer, default=0)
    min_price = Column(Float)

    item = relationship("ItemMaster", back_populates="day_listings")
    datasource = relationship("Datasource")
