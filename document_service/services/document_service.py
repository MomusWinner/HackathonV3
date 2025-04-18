import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Protocol
from uuid import UUID
from io import BytesIO

from document_service.models import Document
from document_service.repositories.document_repository import DocumentRepository
from document_service.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    ManyDocumentsResponse, TinyDocumentResponse,
)
import PyPDF2
import re
from decimal import Decimal

from document_service.tasks.ai_tasks import AIRemoteDocumentAnalyzer


class DocumentService:
    def __init__(self, repository: DocumentRepository, financial_category_analyzer: AIRemoteDocumentAnalyzer):
        self.repository = repository
        self.financial_category_analyzer = financial_category_analyzer

    async def create_document(
        self, document: DocumentCreate
    ) -> DocumentResponse:
        new_document = await self.repository.create(document)
        self.financial_category_analyzer.analyze(new_document.id)

        return DocumentResponse.model_validate(new_document)

    async def get_document(self, document_id: UUID) -> Optional[DocumentResponse]:
        document = await self.repository.get(document_id)
        if not document:
            return None
        return DocumentResponse.model_validate(document)

    async def process_account_statement(
        self,
        user_id: UUID,
        pdf_file: bytes,
        bank: Optional[str] = 'tbank',
    ) -> ManyDocumentsResponse:
        dict_documents = self._parse_account_stmt(pdf_file, user_id=user_id, bank=bank)
        await self.repository.create_account_stmt(dict_documents)

        for ts in dict_documents:
            self.financial_category_analyzer.analyze(ts['id'])

        return ManyDocumentsResponse(
            total=len(dict_documents),
            results=reversed(sorted(
                [DocumentResponse.model_validate(ts) for ts in dict_documents],
                key=lambda t: t.receipt_date
            )),
        )

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

    async def get_categories_data(self, user_id: UUID):
        documents, total = await self.repository.get_all(
            user_id=user_id,
            limit=10_000_000
        )
        res = {}
        for ts in documents:
            if not res.get(ts.category):
                res[ts.category] = 1
            else:
                res[ts.category] += 1

        return res, total


    def _parse_account_stmt(self, pdf_content: bytes, user_id: UUID, format: str):
        if format == 'pdf':
            with BytesIO(pdf_content) as pdf_file:  # noqa
                read_pdf = PyPDF2.PdfReader(pdf_file)
                full_text = ""
                for page in read_pdf.pages:
                    full_text += page.extract_text()
            return full_text

        raise NotImplementedError

    async def get_financial_safety_cushion(self, user_id: UUID) -> tuple[float, float]:
        avg_withdrawal = await self.repository.get_avg_withdrawal_by_user(user_id)
        last_balance = await self.repository.get_user_current_balance(user_id)
        if not (last_balance and avg_withdrawal):
            return 0, 0

        return last_balance, avg_withdrawal * 3

    #
    # async def update_ts_category(self, document_id: UUID, category: str):
    #     ts = await self.repository.get(document_id)
    #     if ts is None:
    #         return None
    #
    #     ts.category = category
    #     avg = await self.repository.get_avg_withdrawal_by_category(
    #         user_id=ts.user_id,
    #         category=ts.category,
    #     )
    #     if (category != 'Salary') and (avg is not None) and avg != 0:
    #         coef = (ts.withdraw - avg) / avg
    #         if coef > 20:
    #             coef = 5
    #         elif coef > 10:
    #             coef = 3
    #         elif coef > 5:
    #             coef = 2
    #         else:
    #             coef = 1
    #         ts.expediency = coef
    #
    #     await self.repository.save(ts)
    #     await self.repository.add_edited(document=Editeddocument(
    #         id=ts.id,
    #         user_id=ts.user_id,
    #         entry_date =ts.receipt_date,
    #         receipt_date = ts.receipt_date,
    #         withdraw=ts.withdraw,
    #         deposit=ts.deposit,
    #         created_at=datetime.now(),
    #         new_category=category,
    #         balance=ts.balance,
    #     ))
    #     self.financial_category_analyzer.fit_model()
    #     return documentResponse.model_validate(ts)

    @staticmethod
    def _date_from_str(date_str: str):
        date_str = date_str.strip()
        updated_year = '20' + date_str.split('.')[-1]
        date_str = '.'.join(date_str.split('.')[:2]) + '.' + updated_year
        return datetime.strptime(date_str, '%d.%m.%Y')
