from typing import Optional
from uuid import UUID
from io import BytesIO
import PyPDF2

from document_service.repositories.document_repository import DocumentRepository
from document_service.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    ManyDocumentsResponse, TinyDocumentResponse,
)
from document_service.utils.file_content_extractors import extract_pdf_content, extract_pptx_content_with_images, \
    extract_pptx_text, extract_pdf_text, extract_docx_content_with_images, extract_docx_text

from document_service.tasks.ai_tasks import AIRemoteDocumentAnalyzer


class DocumentService:
    def __init__(self, repository: DocumentRepository, financial_category_analyzer: AIRemoteDocumentAnalyzer):
        self.repository = repository
        self.financial_category_analyzer = financial_category_analyzer

    async def create_document(
        self, document: DocumentCreate
    ) -> DocumentResponse:
        new_document = await self.repository.create(document)

        print('Successfully added to db')
        file_format = document.filename.split('.')[1]
        document_text = self._get_document_text(
            document.content, file_format, document.analyze_images
        )

        self.financial_category_analyzer.analyze(
            new_document.id,
            document_text,
            document.show_tags,
            document.show_topics,
            document.show_recommendations,
            document.prompt,
        )

        return new_document.id

    async def get_document(self, document_id: UUID) -> Optional[DocumentResponse]:
        document = await self.repository.get(document_id)
        if not document:
            return None
        return DocumentResponse.model_validate(document)

    async def get_documents_by_user_id(
        self,
        user_id: UUID,
        limit: int,
        offset: int,
    ) -> ManyDocumentsResponse:
        documents, total = await self.repository.get_all(
            user_id=user_id,
            skip=offset,
            limit=limit
        )
        return ManyDocumentsResponse(
            total=total,
            results=[TinyDocumentResponse.model_validate(doc) for doc in documents],
        )


    def _get_document_text(self, file_content: bytes, file_format: str, analyze_images: bool):
        full_text = ""
        if file_format == 'pdf':
            full_text = extract_pdf_content(file_content) if analyze_images else extract_pdf_text(file_content)

        if file_format == 'pptx':
            full_text = extract_pptx_content_with_images(file_content) if analyze_images else extract_pptx_text(file_content)

        if file_format == "docx":
            full_text = extract_docx_content_with_images(file_content) if analyze_images else extract_docx_text(file_content)

        print('Extracted:', full_text)
        if full_text == "":
            raise NotImplementedError

        return full_text

