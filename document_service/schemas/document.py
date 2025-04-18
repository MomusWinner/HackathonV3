
from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict, Field


class DocumentCreate(BaseModel):
    user_id: UUID4
    filename: str
    content: bytes
    show_tags: bool
    show_topics: bool
    analyze_images: bool
    prompt: str | None = None
    show_recommendations: bool


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    title: str | None
    tags: list[str] | None
    recommendations: str | None
    summary: str | None
    processing_status: str
    created_at: datetime

    ws_url: str | None = Field(None)


class TinyDocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    processing_status: str


class ManyDocumentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    results: list[TinyDocumentResponse]
