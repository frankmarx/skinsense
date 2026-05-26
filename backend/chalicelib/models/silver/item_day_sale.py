from sqlalchemy import Column, String, Float, Integer, Date, ForeignKey, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from chalicelib.db import Base

class ItemDaySales(Base):
    __tablename__ = 'item_day_sale'

    item_id = Column(String, primary_key=True)
    datasource_id = Column(String, primary_key=True)
    day = Column(Date, primary_key=True)
    
    sell_count = Column(Integer, default=0)
    min_price = Column(Float)

    __table_args__ = (
        {'schema': 'skinsense'},
        ForeignKeyConstraint(
            ['item_id'],
            ['skinsense.item_master.item_id'],
        ),
        ForeignKeyConstraint(
            ['datasource_id'],
            ['skinsense.datasource.datasource_id'],
        ),
    )


    item = relationship("ItemMaster", back_populates="day_sales")
    datasource = relationship("Datasource", back_populates="day_sales")
