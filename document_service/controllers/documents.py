from contextlib import suppress
from datetime import datetime
from typing import Annotated, Optional
from uuid import UUID

from dishka import FromDishka
from dishka.integrations.fastapi import DishkaRoute
from fastapi import APIRouter, HTTPException, status, Query, UploadFile, Form, WebSocket
from fastapi.responses import Response
from redis.asyncio import Redis

from document_service.schemas.document import DocumentCreate, DocumentResponse, ManyDocumentResponse
from document_service.services.document_service import DocumentService
from document_service.utils.cache import cache
from document_service.utils.metrics import (
    CREATE_DOCUMENT_METHOD_DURATION,
    GET_ALL_DOCUMENTS_METHOD_DURATION,
    measure_latency,
)

router = APIRouter(route_class=DishkaRoute)


@router.post("/documents/", response_model=DocumentResponse)
@measure_latency(CREATE_DOCUMENT_METHOD_DURATION)
async def create_transaction(
        file: UploadFile,
        show_tags: Annotated[bool, Form()],
        show_keywords: Annotated[bool, Form()],
        analyze_images: Annotated[bool, Form()],
        show_recommendations: Annotated[bool, Form()],
        service: FromDishka[DocumentService],

):
    content = await file.read()
    new_document_id = await service.create_document(DocumentCreate(
        content=content,
        show_tags=show_tags,
        show_keywords=show_keywords,
        analyze_images=analyze_images,
        show_recommendations=show_recommendations,
    ))

    return {'url': f"ws://localhost:8000/api/v1/analyzes/{new_document_id}"}

@router.websocket("/analyzes/{document_id}")
async def receive_analyze(
        websocket: WebSocket,
        document_id: UUID,
):
    await websocket.accept()
    if document_id not in websocket_connections:
        websocket_connections[document_id] = []
    websocket_connections[document_id].append(websocket)

    try:
        while True:
            # Держим соединение открытым
            await websocket.receive_text()
    except Exception as e:
        print(e)
        websocket_connections[document_id].remove(websocket)
        if not websocket_connections[document_id]:
            del websocket_connections[document_id]
    finally:
        with suppress(RuntimeError):
            await websocket.close()


async def send_new_notification_to_user(user_id: str, notification: Response):
    if user_id in websocket_connections:
        for websocket in websocket_connections[user_id]:
            await websocket.send_json(notification.model_dump(mode='json'))


websocket_connections = {}


# @router.get("/documents/", response_model=ManyTransactionsResponse)
# @measure_latency(GET_ALL_TRANSACTIONS_METHOD_DURATION)
# async def create_transaction(
#         user_id: UUID,
#         service: FromDishka[DocumentService],
#         start_date: datetime | None = None,
#         end_date: datetime | None = None,
#         offset: int = 0,
#         limit: int = 10,
# ):
#     user_transactions = await service.get_transactions_by_user_id(
#         user_id=user_id,
#         start_date=start_date,
#         end_date=end_date,
#         limit=limit,
#         offset=offset,
#     )
#     return user_transactions
#
#
# @router.post("/documents/load-account-statement/")
# async def process_account_statement(
#         user_id: Annotated[UUID, Query(...)],
#         bank: Annotated[str, Query(...)],
#         file: UploadFile,
#         service: FromDishka[DocumentService]
# ):
#     content = await file.read()
#     res = await service.process_account_statement(user_id=user_id, bank=bank, pdf_file=content)
#     return res
#
#
# @router.get("/documents/{transaction_id}", response_model=TransactionResponse)
# @cache(ttl=2)
# async def get_transaction(
#         transaction_id: UUID,
#         redis_client: FromDishka[Redis],  # noqa
#         service: FromDishka[DocumentService]
# ):
#     transaction = await service.get_transaction(transaction_id)
#     if not transaction:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
#     return transaction
#
#
# # @router.patch("/documents/{transaction_id}", response_model=TransactionResponse)
# # async def update_transaction_category(
# #         transaction_id: UUID,
# #         category: str,
# #         service: FromDishka[TransactionService]
# # ):
# #     res = await service.update_ts_category(transaction_id, category)
# #     return res
# #
# # @router.get('/documents/financial-safety-cushion')
# # async def get_financial_safety_cushion(
# #         user_id: Annotated[UUID, Query(...)],
# #         service: FromDishka[TransactionService]
# # ):
# #     res = await service.get_financial_safety_cushion(user_id=user_id)
# #     return res
# #
# #
# # @router.get('/documents/get-categories-data')
# # async def get_financial_safety_cushion(
# #         user_id: Annotated[UUID, Query(...)],
# #         service: FromDishka[TransactionService]
# ):
#     res = await service.get_categories_data(user_id=user_id)
#     return res

