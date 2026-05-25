from sqlalchemy import Column, String, Float, Date, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from chalicelib.db import Base

class ItemListingDetail(Base):
    __tablename__ = 'item_listing_detail'

    listing_id = Column(String, primary_key=True)
    item_id = Column(String, ForeignKey('item_master.item_id'), nullable=False)
    datasource_id = Column(String, ForeignKey('datasource.datasource_id'), nullable=False)
    day = Column(Date)
    
    # New requested fields
    listing_created_ts = Column(DateTime)
    listing_type = Column(String)
    list_price = Column(Float)
    def_index = Column(Integer)
    paint_index = Column(Integer)
    paint_seed = Column(Integer)
    float_value = Column(Float)
    is_stattrak = Column(Boolean)
    is_souvenir = Column(Boolean)

    item = relationship("ItemMaster", back_populates="listing_details")
    datasource = relationship("Datasource")
