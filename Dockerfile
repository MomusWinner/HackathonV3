FROM python:3.12-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN apt update && apt-get install -y poppler-utils

WORKDIR /app
ADD . .

RUN uv sync --frozen --no-cache

CMD ["uv", "run", "uvicorn", "document_service.main:app", "--host", "0.0.0.0", "--port", "8000"]