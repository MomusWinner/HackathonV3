from datetime import datetime

from pydantic import UUID4, BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    user_id: UUID4
    filename: str
    content: bytes
    show_tags: bool
    show_keywords: bool
    analyze_images: bool
    show_recommendations: bool



class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    user_id: UUID4
    title: str
    tags: None | list[str]
    recommendations: str
    summary: str
    processing_status: str
    created_at: datetime


class TinyDocumentResponse(BaseModel):
    id: UUID4
    processing_status: str


class ManyDocumentsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    total: int
    results: list[TinyDocumentResponse]
