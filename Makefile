.PHONY: help prepare install format lint test build publish clean

help:
	@echo "📦 Makefile for cockroachdb-mcp-client"
	@echo ""
	@echo "Available targets:"
	@echo "  prepare     Set up virtualenv and install build tools"
	@echo "  install     Install dependencies in editable mode"
	@echo "  format      Format code using black"
	@echo "  lint        Run static checks with ruff"
	@echo "  test        Run tests with pytest"
	@echo "  build       Build wheel and sdist packages"
	@echo "  publish     Upload to PyPI (requires credentials)"
	@echo "  clean       Remove build and metadata artifacts"

prepare:
	@echo "🔧 Preparing virtual environment..."
	@python3 -m venv .venv
	@. .venv/bin/activate && \
		python -m ensurepip --upgrade && \
		python -m pip install --upgrade pip build

install:
	pip install -e .[dev]

format:
	black cockroachdb_mcp_client 

lint:
	ruff cockroachdb_mcp_client

test:
	pytest tests/

build:
	. .venv/bin/activate && python -m build

publish:
	twine upload dist/*

clean:
	rm -rf dist/ build/ *.egg-info .pytest_cache .mypy_cache .venv
