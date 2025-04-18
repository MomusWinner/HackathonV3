import uuid
from datetime import datetime

from sqlalchemy import UUID, INTEGER, Column, DateTime, DECIMAL, String, ARRAY

from .base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, nullable=False)
    summary = Column(DECIMAL, nullable=False)
    recommendations = Column(DECIMAL, nullable=False)
    processing_status = Column(String, default="in_progress") # in_progress, completed
    tags = Column(ARRAY(String), nullable=True)
    expediency = Column(INTEGER, nullable=True)
    balance = Column(DECIMAL, nullable=True)
    created_at = Column(DateTime, default=datetime.now)