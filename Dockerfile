# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=0
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_CACHE_DIR=/opt/poetry_cache

# Declare environment variables for Railway
ARG CSRF_TRUSTED_ORIGINS

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        gcc \
        python3-dev \
        musl-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml poetry.lock* requirements.txt ./

# Install dependencies - try Poetry first, fallback to pip
RUN pip install poetry==1.8.3 && \
    poetry config virtualenvs.create false && \
    poetry config virtualenvs.in-project false && \
    (poetry install --only=main --no-root || pip install -r requirements.txt) && \
    rm -rf $POETRY_CACHE_DIR

# Copy project
COPY . /app/

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser && chown -R appuser /app
USER appuser

# Collect static files (with dummy database URL since we don't need DB for static files)
RUN poetry run python manage.py collectstatic --noinput

# Expose port (Railway will set PORT environment variable)
EXPOSE 8080

# Make setup.sh executable and run script
RUN chmod +x /app/setup.sh && /app/setup.sh

# Start gunicorn
ENTRYPOINT ["sh", "-c", "gunicorn weuro2025.wsgi:application"]
