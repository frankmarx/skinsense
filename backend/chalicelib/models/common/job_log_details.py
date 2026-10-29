from sqlalchemy import Column, String, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from chalicelib.db import Base

class JobLogDetails(Base):
    __tablename__ = 'job_log_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(UUID(as_uuid=True), nullable=False)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    action = Column(String, nullable=False)
    status = Column(String, nullable=False)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_job_log_job_id', 'job_id'),
        Index('idx_job_log_event_id', 'event_id'),
        {'schema': 'skinsense'}
    )
