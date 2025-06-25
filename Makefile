# BioCode Makefile

.PHONY: help install test lint format clean migrate

help:
	@echo "Available commands:"
	@echo "  install    Install dependencies"
	@echo "  test       Run tests"
	@echo "  lint       Run linters"
	@echo "  format     Format code"
	@echo "  clean      Clean build artifacts"
	@echo "  migrate    Run migration script"
	@echo "  run        Run the application"

install:
	poetry install

test:
	pytest tests/ -v --cov=src/biocode

lint:
	ruff check src/ tests/
	mypy src/

format:
	black src/ tests/
	isort src/ tests/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage .mypy_cache

migrate:
	python migrate_to_new_structure.py

run:
	python -m biocode.interfaces.api

dev:
	docker-compose -f deployment/docker/docker-compose.yml up
