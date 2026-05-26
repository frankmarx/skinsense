from sqlalchemy import Column, String, DateTime, Integer
from sqlalchemy.sql import func
from chalicelib.db import Base

class FeedLoaderLog(Base):
    __tablename__ = 'feed_loader_log'
    __table_args__ = {'schema': 'skinsense'}

    id = Column(Integer, primary_key=True, autoincrement=True)
    jobid = Column(String, nullable=False)
    datasource_id = Column(String, nullable=False)
    feed_name = Column(String, nullable=False)
    action = Column(String, nullable=False)
    time_logged = Column(DateTime, server_default=func.now())
