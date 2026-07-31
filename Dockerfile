FROM python:3.12-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

# Dependency files first -- this layer only rebuilds when deps actually change
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-dev

# Now the rest of the source
COPY . .
RUN chmod +x scripts/entrypoint.sh

ENV DAGSTER_HOME=/app/dagster_home
RUN mkdir -p $DAGSTER_HOME

EXPOSE 3000

ENTRYPOINT ["/app/scripts/entrypoint.sh"]
