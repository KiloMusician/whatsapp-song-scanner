.PHONY: help up down restart logs test lint format clean install migrate backup

help:
	@echo "WhatsApp Song Scanner - Development Commands"
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make up           - Start all Docker services"
	@echo "  make down         - Stop all Docker services"
	@echo "  make restart      - Restart all services"
	@echo "  make logs         - Follow logs"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linters"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean cache and temp files"
	@echo "  make migrate      - Run database migrations"
	@echo "  make backup       - Backup database"

install:
	pip install -r requirements.txt -r requirements-dev.txt
	mkdir -p data/logs data/cache data/temp data/exports

up:
	docker-compose -f docker/docker-compose.yml up -d

down:
	docker-compose -f docker/docker-compose.yml down

restart:
	docker-compose -f docker/docker-compose.yml restart

logs:
	docker-compose -f docker/docker-compose.yml logs -f

test:
	pytest -v --cov=src

lint:
	flake8 src tests
	mypy src

format:
	black src tests
	isort src tests

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov
	rm -rf data/cache/* data/temp/*

migrate:
	docker-compose -f docker/docker-compose.yml exec song-scanner-bot alembic upgrade head

backup:
	./scripts/maintenance/backup_database.sh
