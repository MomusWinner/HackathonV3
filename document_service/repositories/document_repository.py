from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text, desc

from document_service.models.document import Document
from document_service.schemas.document import DocumentCreate


class DocumentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, document: DocumentCreate) -> Document:
        db_document = Document(user_id=document.user_id)
        self.session.add(db_document)
        await self.session.commit()
        await self.session.refresh(db_document)
        return db_document

    async def save(self, document: Document):
        self.session.add(document)
        await self.session.commit()

    async def create_account_stmt(self, documents: list):
        for ts in documents:
            self.session.add(Document(**ts))
        await self.session.commit()

    async def get(self, document_id: UUID) -> Optional[Document]:
        result = await self.session.execute(
            select(Document).filter(Document.id == document_id)
        )
        return result.scalars().first()

    async def get_all(
            self,
            user_id: UUID,
            skip: int = 0,
            limit: int = 10,
    ) -> tuple[list[Document], int]:
        base_query = select(Document).filter(Document.user_id == user_id)

        data_query = base_query.order_by(Document.id.desc()).offset(skip).limit(limit)
        data_result = await self.session.execute(data_query)
        documents = list(data_result.scalars().all())

        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await self.session.execute(count_query)
        total = count_result.scalar()

        return documents, total

    # async def get_all_edited(self):
    #     stmt = select(Editeddocument)
    #     res = await self.session.execute(stmt)
    #     return res.scalars().all()
    #
    # async def drop_edited(self):
    #     stmt = delete(Editeddocument)
    #     await self.session.execute(stmt)
    #     await self.session.commit()
    #
    # async def add_edited(self, document: Editeddocument):
    #     self.session.add(document)
    #     await self.session.commit()

    async def get_avg_withdrawal_by_category(self, user_id: UUID, category: str):
        res = await self.session.execute(text(
            """
            select avg(withdraw) from documents
            where user_id = :user_id and
            category = :cat and 
            entry_date between (now() - interval '1 month') and now()
            """),
            {'user_id': user_id, 'cat': category}
        )
        result = res.fetchone()
        return result[0] if result else None

    async def get_avg_withdrawal_by_user(self, user_id: UUID):
        res = await self.session.execute(text(
            """
            select avg(withdraw) from documents
            where user_id = :user_id and
            entry_date between (now() - interval '3 month') and now()
            """),
            {'user_id': user_id}
        )
        result = res.fetchone()
        return result[0] if result else None

    async def get_user_current_balance(self, user_id: UUID):
        res = await self.session.execute(select(Document).where(Document.user_id == user_id).order_by(desc(Document.receipt_date)).limit(1))
        last_ts = res.scalar_one_or_none()
        if last_ts:
            return last_ts.balance

    async def get_oldest_ts(self, user_id: UUID):
        res = await self.session.execute(text(
            """
            select created_at from documents where user_id=:user_id order by created_at desc limit 1
            """),
            {'user_id': user_id}
        )
        return res.fetchone()


    async def update_status(
        self, document_id: UUID, status: str
    ) -> Optional[Document]:
        document = await self.get(document_id)
        if not document:
            return None
        document.processing_status = status
        await self.session.commit()
        await self.session.refresh(document)
        return document

    async def update_analysis(
        self,
        document_id: UUID,
        title: str,
        theme: str,
        recommendations: str,
        summary: str,
        tags: list[str],
        blocks: list[dict],
        status: str
    ) -> Optional[Document]:
        document = await self.get(document_id)
        if not document:
            return None
        document.title = title
        document.theme = theme
        document.recommendations = recommendations
        document.summary = summary
        document.tags = tags
        document.blocks = blocks
        document.processing_status = status
        await self.session.commit()
        await self.session.refresh(document)
        return document
