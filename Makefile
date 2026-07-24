.PHONY: install run test test-cov lint format format-check type security complexity check clean

APP := delivery_service.main:app
SRC := src
TESTS := tests


install:
	uv sync


run:
	uv run uvicorn $(APP) --reload --app-dir $(SRC)


test:
	uv run pytest $(TESTS) -v


test-cov:
	uv run pytest $(TESTS) \
		--cov=$(SRC)/delivery_service \
		--cov-report=term-missing \
		--cov-report=html


lint:
	uv run ruff check $(SRC) $(TESTS)


format:
	uv run ruff format $(SRC) $(TESTS)
	uv run ruff check $(SRC) $(TESTS) --fix


format-check:
	uv run ruff format $(SRC) $(TESTS) --check


type:
	uv run mypy $(SRC)


security:
	uv run bandit -r $(SRC)


complexity:
	uv run radon cc $(SRC) -a -s
	uv run radon mi $(SRC) -s


check: format-check lint type security test


clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -f .coverage
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete