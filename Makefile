.PHONY: generate
generate:
	alembic revision --m='init' --autogenerate

.PHONY: migrate
migrate:
	alembic upgrade head

.PHONY:	black
black:
	poetry run black bot/

.PHONY: isort
isort:
	poetry run isort bot/

.PHONY: flake
flake:
	poetry run flake8 bot/

.PHONY: lint
lint: black isort flake