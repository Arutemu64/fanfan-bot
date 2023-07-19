.PHONY: generate
generate:
	alembic revision --m='init' --autogenerate

.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY:	black
black:
	poetry run black src/

.PHONY: isort
isort:
	poetry run isort src/

.PHONY: flake
flake:
	poetry run flake8 src/

.PHONY: lint
lint: black isort flake