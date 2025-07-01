# Use Python 3.11 slim image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=0
ENV POETRY_VIRTUALENVS_CREATE=false
ENV POETRY_CACHE_DIR=/opt/poetry_cache

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
RUN DJANGO_SETTINGS_MODULE=weuro2025.settings \
    DATABASE_URL=sqlite:///tmp/dummy.db \
    python manage.py collectstatic --noinput

# Expose port (Railway will set PORT environment variable)
EXPOSE 8000

# Run migrations 
RUN python manage.py migrate 

# Run FBRef sync to initialise database
RUN python manage.py sync_fbr_data

# Start gunicorn
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-8000} weuro2025.wsgi:application"]
