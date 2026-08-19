.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help install lint format test test-unit test-integration check migration upgrade downgrade up down logs shell clean

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies and the git hooks
	uv sync
	uv run pre-commit install --install-hooks

format: ## Autofix and format
	uv run ruff check --fix .
	uv run ruff format .

lint: ## Ruff, ty and the architecture contracts
	uv run ruff check .
	uv run ruff format --check .
	uv run ty check
	uv run lint-imports

test: ## Run the whole test suite
	uv run pytest

test-unit: ## Run the tests that need no database
	uv run pytest tests/unit

test-integration: ## Run the tests that need PostgreSQL
	uv run pytest tests/integration

check: lint test ## Everything CI runs

migration: ## Autogenerate a revision: make migration m="add streaks"
	uv run alembic revision --autogenerate -m "$(m)"

upgrade: ## Apply all migrations
	uv run alembic upgrade head

downgrade: ## Roll back the last migration
	uv run alembic downgrade -1

up: ## Start the Docker stack
	docker compose up --build -d

down: ## Stop the Docker stack
	docker compose down

logs: ## Tail the API logs
	docker compose logs -f api

shell: ## Open a shell in the API container
	docker compose exec api bash

clean: ## Remove caches
	rm -rf .ruff_cache .pytest_cache .ty_cache htmlcov .coverage
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
