FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

# Dependency layer cached separately from source so code edits don't force a re-resolve.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src
RUN uv sync --frozen --no-dev

COPY . .
RUN mkdir -p /app/.dagster_home /app/lake /app/warehouse

ENV DAGSTER_HOME=/app/.dagster_home
ENV PYTHONUNBUFFERED=1

EXPOSE 3000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
