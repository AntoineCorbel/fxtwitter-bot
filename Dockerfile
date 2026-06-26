FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:0.7.13 /uv /bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

CMD ["uv", "run", "main.py"]
