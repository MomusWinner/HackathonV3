from typing import Optional
from uuid import UUID
from io import BytesIO

from document_service.repositories.document_repository import DocumentRepository
from document_service.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    ManyDocumentsResponse, TinyDocumentResponse,
)
from document_service.utils.pdf_extractor import extract_pdf_content


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
        document_text = self._get_document_text(document.content, file_format)
        print(document_text)

        self.financial_category_analyzer.analyze(
            new_document.id,
            document_text,
            document.show_tags,
            document.show_keywords,
            document.analyze_images,
            document.show_recommendations,
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


    def _get_document_text(self, file_content: bytes, file_format: str):
        if file_format == 'pdf':
            return extract_pdf_content(file_content)

        raise NotImplementedError
