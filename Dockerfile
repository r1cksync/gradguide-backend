FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p /app/data /app/data/backup /app/chroma_db
COPY . .
RUN chmod -R 777 /app/data /app/chroma_db

CMD uvicorn main:app --host 0.0.0.0 --port $PORT