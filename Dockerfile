# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PORT=8000

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc libffi-dev g++ && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /app/data /app/data/backup /app/chroma_db

# Copy the current directory contents into the container
COPY . .

# Make sure the data directory is accessible
RUN chmod -R 777 /app/data
RUN chmod -R 777 /app/chroma_db

# Run using the PORT environment variable which will be set by Render
CMD uvicorn main:app --host 0.0.0.0 --port $PORT