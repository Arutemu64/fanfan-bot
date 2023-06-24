.PHONY: generate
generate:
	alembic revision --m='init' --autogenerate

.PHONY: migrate
migrate:
	alembic upgrade head