from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from chalicelib.db import Base

class Datasource(Base):
    __tablename__ = 'datasource'
    __table_args__ = {'schema': 'skinsense'}

    datasource_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)

    # Relationship to items belonging to this datasource
    day_sales = relationship("ItemDaySales", back_populates="datasource")
    day_listings = relationship("ItemDayListing", back_populates="datasource")
    listing_details = relationship("ItemListingDetail", back_populates="datasource")
