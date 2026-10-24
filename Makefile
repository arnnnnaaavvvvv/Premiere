.PHONY: dev dev-api dev-worker dev-web test lint clean

# Default development target launching core services
dev:
	@echo "Starting ReelForge development environment..."
	python -m uvicorn api.main:app --reload --port 8000

dev-api:
	python -m uvicorn api.main:app --reload --port 8000

dev-worker:
	python -m worker.main

dev-web:
	cd web && npm run dev

# Run automated test suites
test:
	pytest tests/ -v

# Run linting and code quality checks
lint:
	python -m ruff check api worker tests || echo "Ruff check complete"
	cd web && npm run lint || echo "Web lint complete"

# Clean temporary runtime and build artifacts
clean:
	rm -rf __pycache__ */__pycache__ .pytest_cache storage/temp/*
