from sqlalchemy import Column, String, DateTime, Integer, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from chalicelib.db import Base

class EventLogDetails(Base):
    __tablename__ = 'event_log_details'

    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String, nullable=True)
    source = Column(String, nullable=False)
    start_time = Column(DateTime, server_default=func.now())
    end_time = Column(DateTime, nullable=True)

    __table_args__ = (
        Index('idx_event_log_event_id', 'event_id'),
        {'schema': 'skinsense'}
    )
