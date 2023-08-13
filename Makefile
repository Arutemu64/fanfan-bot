.PHONY:	black
black:
	poetry run black src/ scripts/

.PHONY: isort
isort:
	poetry run isort src/ scripts/

.PHONY: flake
flake:
	poetry run flake8 src/ scripts/

.PHONY: lint
lint: black isort flake

# Alembic utils
.PHONY: generate
generate:
	alembic revision --m="$(NAME)" --autogenerate

.PHONY: migrate
migrate:
	alembic upgrade head