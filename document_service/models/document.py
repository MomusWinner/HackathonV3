import uuid
from datetime import datetime

from sqlalchemy import UUID, Column, DateTime, String, ARRAY
from sqlalchemy.dialects.postgresql import JSON

from .base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID, nullable=False)
    title = Column(String, nullable=True)
    theme = Column(String, nullable=True)
    recommendations = Column(String, nullable=True)
    summary = Column(String, nullable=True)
    tags = Column(ARRAY(String), nullable=True)
    blocks = Column(ARRAY(JSON), nullable=True)
    processing_status = Column(String, default="processing") # processing, completed
    created_at = Column(DateTime, default=datetime.now)
