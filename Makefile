.PHONY: install dev shell clean test lint format run migrate collectstatic docker-build docker-run

# Installation and setup
install:
	poetry install

dev:
	poetry install --with dev

shell:
	poetry shell

# Development commands
run:
	poetry run python manage.py runserver

migrate:
	poetry run python manage.py makemigrations
	poetry run python manage.py migrate

collectstatic:
	poetry run python manage.py collectstatic --noinput

createsuperuser:
	poetry run python manage.py createsuperuser

sample-data:
	poetry run python manage.py create_sample_data

sync-data:
	poetry run python manage.py sync_fbr_data

process-round:
	poetry run python manage.py process_round

# Code quality
test:
	poetry run pytest

lint:
	poetry run flake8 .
	poetry run isort --check-only .
	poetry run black --check .

format:
	poetry run isort .
	poetry run black .

# Docker commands
docker-build:
	docker build -t weuro2025-game .

docker-run:
	docker-compose up --build

docker-dev:
	docker-compose -f docker-compose.dev.yml up --build

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +

# Export requirements.txt for deployment platforms that don't support Poetry
export-requirements:
	poetry export --format requirements.txt --output requirements.txt --without-hashes

# Help
help:
	@echo "Available commands:"
	@echo "  install          - Install dependencies"
	@echo "  dev              - Install with dev dependencies"
	@echo "  shell            - Activate Poetry shell"
	@echo "  run              - Run development server"
	@echo "  migrate          - Make and apply migrations"
	@echo "  collectstatic    - Collect static files"
	@echo "  createsuperuser  - Create Django superuser"
	@echo "  sample-data      - Create sample data"
	@echo "  sync-data        - Sync data from FBR API"
	@echo "  process-round    - Process round logic"
	@echo "  test             - Run tests"
	@echo "  lint             - Run linting checks"
	@echo "  format           - Format code with black and isort"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-run       - Run with docker-compose"
	@echo "  docker-dev       - Run development docker-compose"
	@echo "  clean            - Remove Python cache files"
	@echo "  export-requirements - Export requirements.txt"
