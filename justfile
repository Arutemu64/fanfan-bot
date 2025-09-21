# Ruff check
ruff-check:
	ruff check src/fanfan --respect-gitignore --fix --unsafe-fixes

# Ruff format
ruff-format:
	ruff format src/fanfan --respect-gitignore

# Lint (format + check)
lint: ruff-format ruff-check

# Install everything
install:
    uv sync --all-groups

# Alembic utils
generate MIGRATION_NAME:
	alembic revision --autogenerate -m="{{MIGRATION_NAME}}"

migrate:
    alembic upgrade head
    python -m fanfan.main.migration