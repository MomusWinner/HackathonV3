import asyncio
import os
from collections.abc import AsyncGenerator
from uuid import UUID

from celery import Celery
from dishka import Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from document_service.config import load_config
from document_service.repositories.document_repository import DocumentRepository

from document_service.utils.metrics import TOTAL_MESSAGES_PRODUCED

import json

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
        show_recommendations: bool,
        prompt: str,
):
    async def inner():
        print('Processing document {}'.format(document_id))
        print('Params:', document_text, show_tags, show_topics, analyze_images, show_recommendations, prompt)

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }



        prompt2 = f"""
        <main-prompt>
        Analyze the provided document-presentation and complete teh following tasks, writing a structured JSON answer IN THE LANGUAGE OF THE DOCUMENT. Also take into considiration the user suggestions
        User's additional instruction: {prompt}
        </main-prompt>
        <tasks>    
        - Analysis of structure and content
        - Describe the current structure of the document (sections, subsections, logical blocks).
        - Indicate whether the sequence of slides/sections corresponds to the purpose of the presentation.
        {'- Formulate 3-5 main tags that the document conveys' if show_tags else ''}.
        - Create a short summary (up to 150 words) that reflects the essence of the presentation.
        - Optimize design and logic
        - Suggest changes to improve the visual design (fonts, graphics, lists).
        - Eliminate contradictions in the narrative, if any.
        - Defining the topic
        {'- Indicate the main theme of the document and secondary thematic lines (if any).' if show_topics else ''}
        {'- Recommendations for improvement' if show_recommendations else ''}
        - Make a list of 3-7 specific edits for the structure (for example: combine slides 5-6, add a section "Use examples", move the "Statistics" block to the beginning).
        - Add a general conclusion.
        Answer format:

        - Clear points with subheadings.
        - Conciseness, use of bulleted lists.
        {'- All recommendations must be practice-oriented and easy to implement.' if show_recommendations else ''}
        </tasks>
    <json-schema>
    {{
      "title": "title",
      "topic": "markdown topics",
      "summary": "markdown summary"
      "recommendations": "markdown recommendations",
      "blocks": [
        {{
          "title": "block title",
          "summary": "block markdown summary"
        }}
      ],
      "tags": ["file tags, one word"]
    }}
    </json-schema>
    """

        format = {
            "type": "json_schema",
            "json_schema": {
                "name": "analyzed_document",
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string"
                        },
                        "theme": {
                            "type": "string"
                        },
                        "recommendations": {
                            "type": "string"
                        },
                        "summary": {
                            "type": "string"
                        },
                        "tags": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                        },
                        "blocks": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string"
                                    },
                                    "summary": {
                                        "type": "string"
                                    }
                                },
                                "required": ["title", "summary"],
                                "additionalProperties": False
                            }
                        }
                    },
                    "required": ["title", "theme", "summary", "recommendations", "tags", "blocks"],
                    "additionalProperties": False
                },
                "strict": True
            }
        }

        messages = [{
            "role": "system",
            "content": prompt2,
            # "temperature": 0.3,
            # "max_tokens": len(text) // 2
        }, {
            "role": "user",
            "content": extra_promt
        }, {
            "role": "user",
            "content": text
        }]

        payload = {
            "model": cfg.openapi.gpt_model,
            "messages": messages,
            "response_format": format
        }

        try:
            response = requests.post(
                cfg.openapi.api_url,
                headers=headers,
                json=payload,
            )
            results = response.json()['choices'][0]['message']['content']
        except Exception as e:
            print(e)

        repo = await container.get(DocumentRepository)
        await repo.update_analysis(status='completed', **results)

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
