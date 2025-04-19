import asyncio
from contextlib import suppress
from typing import Annotated
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute, inject
from fastapi import APIRouter, HTTPException, status, UploadFile, Form, WebSocket
from redis.asyncio import Redis

from document_service.repositories.document_repository import DocumentRepository
from document_service.schemas.document import DocumentCreate, DocumentResponse, \
    ManyDocumentsResponse
from document_service.services.document_service import DocumentService
from document_service.tasks.ai_tasks import AIRemoteDocumentAnalyzer
from document_service.utils.cache import cache
from document_service.utils.metrics import (
    CREATE_DOCUMENT_METHOD_DURATION,
    GET_ALL_DOCUMENTS_METHOD_DURATION,
    measure_latency,
)

router = APIRouter(route_class=DishkaRoute)


@router.post("/documents/")
@measure_latency(CREATE_DOCUMENT_METHOD_DURATION)
async def create_documents(
        file: UploadFile,
        user_id: Annotated[str, Form()],
        show_tags: Annotated[bool, Form()],
        show_topics: Annotated[bool, Form()],
        analyze_images: Annotated[bool, Form()],
        show_recommendations: Annotated[bool, Form()],
        prompt: Annotated[str, Form()],
        service: FromDishka[DocumentService],

):
    content = await file.read()
    new_document_id = await service.create_document(DocumentCreate(
        content=content,
        user_id=user_id,
        filename=file.filename,
        show_tags=show_tags,
        show_topics=show_topics,
        analyze_images=analyze_images,
        prompt=prompt,
        show_recommendations=show_recommendations,
    ))
    return {
        "id": new_document_id,
        'url': f"ws://localhost:8000/api/v1/analyzes/{new_document_id}"
    }


@router.websocket("/analyzes/{document_id}")
@inject
async def receive_analyze(
        websocket: WebSocket,
        document_id: UUID,
        session_maker: FromDishka[async_sessionmaker]
):

    await websocket.accept()
    if document_id not in websocket_connections:
        websocket_connections[document_id] = []
    websocket_connections[document_id].append(websocket)

    async with session_maker() as session:
        service = DocumentService(
            DocumentRepository(session),
            AIRemoteDocumentAnalyzer()
        )

        try:
            while True:
                # Держим соединение открытым
                # await websocket.receive_text()
                print(f'Checking database for {document_id}..')
                document = await service.get_document(document_id)
                if document is not None and document.processing_status == 'completed':
                    await websocket.send_json(data=document.model_dump(mode='json'))
                await asyncio.sleep(2)
        except Exception as e:
            print(e)
            websocket_connections[document_id].remove(websocket)
            if not websocket_connections[document_id]:
                del websocket_connections[document_id]
        finally:
            with suppress(RuntimeError):
                await websocket.close()


websocket_connections = {}


@router.get("/documents/", response_model=ManyDocumentsResponse)
@measure_latency(GET_ALL_DOCUMENTS_METHOD_DURATION)
async def create_document(
        user_id: UUID,
        service: FromDishka[DocumentService],
        offset: int = 0,
        limit: int = 10,
):
    user_documents = await service.get_documents_by_user_id(
        user_id=user_id,
        limit=limit,
        offset=offset,
    )
    return user_documents


@router.get("/documents/{document_id}", response_model=DocumentResponse)
@cache(ttl=2)
async def get_document(
        document_id: UUID,
        redis_client: FromDishka[Redis],  # noqa
        service: FromDishka[DocumentService]
):
    document = await service.get_document(document_id)
    document.ws_url = f"ws://localhost:8000/api/v1/analyzes/{document.id}"
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document
