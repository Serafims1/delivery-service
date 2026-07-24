# ===============================
# Настройки проекта
# ===============================

APP := delivery_service.main:app
SRC := src
TESTS := tests
PY_SRCS := $(SRC) $(TESTS)

RADON_MIN_MI := 65


# ===============================
# Служебные цели
# ===============================

.PHONY: help install run test test-cov lint format-check type security \
	cc mi complexity fix check pre-commit clean


help:
	@echo "Доступные команды:"
	@echo "  make install      - установить зависимости"
	@echo "  make run          - запустить FastAPI"
	@echo "  make test         - запустить тесты"
	@echo "  make test-cov     - запустить тесты с покрытием"
	@echo "  make lint         - проверить код через Ruff"
	@echo "  make format-check - проверить форматирование"
	@echo "  make type         - проверить типизацию через mypy"
	@echo "  make security     - проверить безопасность через Bandit"
	@echo "  make cc           - проверить цикломатическую сложность"
	@echo "  make mi           - проверить индекс поддерживаемости"
	@echo "  make complexity   - запустить проверки Radon"
	@echo "  make fix          - исправить Ruff-ошибки и форматирование"
	@echo "  make check        - запустить полный quality gate"
	@echo "  make pre-commit   - запустить pre-commit на всех файлах"
	@echo "  make clean        - удалить временные файлы"


# ===============================
# Установка и запуск
# ===============================

install:
	uv sync


run:
	uv run uvicorn $(APP) --reload --app-dir $(SRC)


# ===============================
# Тестирование
# ===============================

test:
	uv run pytest $(TESTS) -v


test-cov:
	uv run pytest $(TESTS) \
		--cov=$(SRC)/delivery_service \
		--cov-report=term-missing \
		--cov-report=html


# ===============================
# Ruff
# ===============================

lint:
	uv run ruff check $(PY_SRCS)


format-check:
	uv run ruff format --check $(PY_SRCS)


fix:
	uv run ruff check $(PY_SRCS) --fix
	uv run ruff format $(PY_SRCS)


# ===============================
# Mypy
# ===============================

type:
	uv run mypy $(PY_SRCS)


# ===============================
# Bandit
# ===============================

security:
	uv run bandit -r $(SRC) \
		-x .venv,venv,build,dist,migrations \
		-ll


# ===============================
# Radon
# ===============================

cc:
	uv run radon cc $(PY_SRCS) -s -a
	@if uv run radon cc $(PY_SRCS) -s | grep -E -- ' - [EF] \('; then \
		echo "Radon CC: обнаружена сложность уровня E/F"; \
		exit 1; \
	else \
		echo "Radon CC: функций уровня E/F нет"; \
	fi


mi:
	@uv run radon mi $(PY_SRCS) -s
	@MI_BAD=$$(uv run radon mi $(PY_SRCS) -s \
		| awk -F '[()]' '/[0-9]+\.[0-9]+/ {print $$2}' \
		| awk '$$1 + 0 < $(RADON_MIN_MI) {print}'); \
	if [ -n "$$MI_BAD" ]; then \
		echo "Radon MI: обнаружен индекс ниже $(RADON_MIN_MI)"; \
		exit 1; \
	else \
		echo "Radon MI: все файлы имеют MI >= $(RADON_MIN_MI)"; \
	fi


complexity: cc mi


# ===============================
# Комплексные проверки
# ===============================

check: format-check lint type security complexity test


pre-commit:
	uv run pre-commit run --all-files


# ===============================
# Очистка
# ===============================

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf htmlcov
	rm -f .coverage
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete