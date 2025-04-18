import asyncio
import os
from collections.abc import AsyncGenerator
from uuid import UUID

from celery import Celery
from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from document_service.config import load_config
from catboost import CatBoostClassifier

from document_service.utils.metrics import TOTAL_MESSAGES_PRODUCED

cfg = load_config(os.getenv('DOCUMENT_SERVICE_CONFIG_PATH', './configs/app.toml'))
celery_app = Celery('tasks', broker=cfg.rabbitmq.uri)


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP)
    def get_engine(self) -> AsyncEngine:
        return create_async_engine(cfg.db.uri, echo=True)

    @provide(scope=Scope.APP)
    def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker:
        return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    @provide(scope=Scope.REQUEST)
    async def get_session(
            self,
            sessionmaker: async_sessionmaker
    ) -> AsyncGenerator[AsyncSession, None, None]:
        async with sessionmaker() as session:
            yield session

    @provide(scope=Scope.APP)
    async def get_model(self) -> CatBoostClassifier:
        return CatBoostClassifier().load_model('model.cbm')


container = make_async_container(DatabaseProvider())

def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)



@celery_app.task
def process_document_analysis(
        document_id: UUID,
        document_text: str,
        show_tags: bool,
        show_keywords: bool,
        analyze_images: bool,
        show_recommendations: bool,
):
    async def inner():
        pass
    return run_async(inner())


# Celery forces doing outer encapsulation
class AIRemoteDocumentAnalyzer:
    def analyze(
            self,
            document_id: UUID,
            document_text: str,
            show_tags: bool,
            show_keywords: bool,
            analyze_images: bool,
            show_recommendations: bool
    ):
        process_document_analysis.delay(
            document_id,
            document_text,
            show_tags,
            show_keywords,
            analyze_images,
            show_recommendations
        )
        TOTAL_MESSAGES_PRODUCED.inc()
