.PHONY: help setup-hooks format lint test up down up-build logs

help:
	@echo "Available commands:"
	@echo "  make setup-hooks - Install developer pre-commit hooks"
	@echo "  make format      - Auto-format Python code (black, isort)"
	@echo "  make lint        - Run linting (flake8)"
	@echo "  make test        - Run backend test suite (pytest)"
	@echo "  make up          - Start all Docker Compose services"
	@echo "  make up-build    - Re-build & start all Docker Compose services"
	@echo "  make down        - Stop & remove all Docker Compose services"
	@echo "  make logs        - Tail logs of all Docker Compose services"

setup-hooks:
	pip install pre-commit
	pre-commit install

format:
	black backend/ ml_pipeline/
	isort backend/ ml_pipeline/

lint:
	flake8 backend/ ml_pipeline/

test:
	pytest backend/tests/

up:
	docker-compose -f deployment/docker-compose.yml up -d

up-build:
	docker-compose -f deployment/docker-compose.yml up -d --build

down:
	docker-compose -f deployment/docker-compose.yml down

logs:
	docker-compose -f deployment/docker-compose.yml logs -f
