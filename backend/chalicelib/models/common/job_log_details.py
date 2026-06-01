from sqlalchemy import Column, String, DateTime, Integer, Index
from sqlalchemy.sql import func
from chalicelib.db import Base

class JobLogDetails(Base):
    __tablename__ = 'job_log_details'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(String, nullable=False, unique=True)
    data_source_id = Column(String, nullable=False)
    event_name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    job_start_time = Column(DateTime, server_default=func.now())
    job_end_time = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_job_log_job_id', 'job_id'),
        {'schema': 'skinsense'}
    )
