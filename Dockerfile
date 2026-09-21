FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml ./
COPY src ./src
COPY migrations ./migrations
COPY alembic.ini ./
RUN pip install --no-cache-dir .

ENV LIFEVERSE_DATABASE_URL=sqlite:////data/lifeverse.db
RUN mkdir -p /data

EXPOSE 8000
CMD ["uvicorn", "lifeverse.api:app", "--host", "0.0.0.0", "--port", "8000"]
