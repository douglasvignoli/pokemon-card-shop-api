.PHONY: up up-test down dev migrate test coverage lint format typecheck check clean

# ── Docker ──────────────────────────────────────────────────────────────────

up:
	docker compose up -d

up-test:
	docker compose up -d db_test

down:
	docker compose down

# ── Aplicação ────────────────────────────────────────────────────────────────

dev: up
	uvicorn main:app --reload

migrate:
	alembic upgrade head

# ── Qualidade de código ──────────────────────────────────────────────────────

lint:
	ruff check .

format:
	ruff format .

typecheck:
	mypy main.py

# ── Testes ───────────────────────────────────────────────────────────────────

test: up-test
	pytest -v

coverage: up-test
	pytest --cov=main --cov-report=term-missing --cov-fail-under=85 -v

# ── Pipeline completo (igual ao CI) ─────────────────────────────────────────

check: lint typecheck coverage

# ── Limpeza ──────────────────────────────────────────────────────────────────

clean:
	docker compose down -v
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	find . -name "*.pyc" -delete
	rm -f .coverage
