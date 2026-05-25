from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from chalicelib.db import Base

class Datasource(Base):
    __tablename__ = 'datasource'

    datasource_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)

    # Relationship to items belonging to this datasource
    items = relationship("ItemMaster", back_populates="datasource")
