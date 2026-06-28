FROM python:3.12-slim

# instalacja uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# zależności najpierw (cache layer)
COPY pyproject.toml .
COPY uv.lock .
RUN uv sync --frozen --no-dev

# kod aplikacji
COPY app/ app/
COPY db/ db/
COPY ml/ ml/

# artefakty ML — baked into image (Opcja B)
COPY models/ models/

ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]