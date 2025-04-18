import asyncio
import os
from collections.abc import AsyncGenerator
from uuid import UUID

from celery import Celery
from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from document_service.config import load_config

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


container = make_async_container(DatabaseProvider())

def run_async(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)



@celery_app.task
def process_document_analysis(
        document_id: UUID,
        document_text: str,
        show_tags: bool,
        show_topics: bool,
        analyze_images: bool,
        show_recommendations: bool,
        prompt: str,
):
    async def inner():
        print('Processing document {}'.format(document_id))
        print('Params:', document_text, show_tags, show_topics, analyze_images, show_recommendations, prompt)
    return run_async(inner())


# Celery forces doing outer encapsulation
class AIRemoteDocumentAnalyzer:
    def analyze(
            self,
            document_id: UUID,
            document_text: str,
            show_tags: bool,
            show_topics: bool,
            analyze_images: bool,
            show_recommendations: bool,
            prompt: str | None
    ):
        process_document_analysis.delay(
            document_id,
            document_text,
            show_tags,
            show_topics,
            analyze_images,
            show_recommendations,
            prompt,
        )
        TOTAL_MESSAGES_PRODUCED.inc()
