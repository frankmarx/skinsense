from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, Index
from sqlalchemy.sql import func
from chalicelib.db import Base

class EventLogDetails(Base):
    __tablename__ = 'event_log_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, ForeignKey('skinsense.job_log_details.job_id'), nullable=False)
    action = Column(String, nullable=False)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_event_log_job_id', 'job_id'),
        {'schema': 'skinsense'}
    )
