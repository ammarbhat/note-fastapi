FROM python:3.12-slim-trixie

COPY --from=ghcr.io/astral-sh/uv:0.12.5 /uv /uvx /bin/

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN uv sync --locked --no-dev --no-install-project

COPY src ./src

EXPOSE 8000

CMD ["sh", "-c", "fastapi run src/crud/main.py --host 0.0.0.0 --port ${PORT:-8000}"]