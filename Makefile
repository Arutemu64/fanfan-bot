.PHONY: help
help:
	@echo "USAGE"
	@echo "  make <commands>"
	@echo ""
	@echo "AVAILABLE COMMANDS"
	@echo "  run		Start the bot (for docker-compose usage)"
	@echo "  project-start Start with docker-compose"
	@echo "  project-stop  Stop docker-compose"
	@echo "  lint		Reformat code"
	@echo "  requirements  Export poetry.lock to requirements.txt"

.PHONY: ruff-check
ruff-check:
	uv run ruff check fanfan/ --respect-gitignore --fix

.PHONY: ruff-format
ruff-format:
	uv run ruff format fanfan/ --respect-gitignore

.PHONY: lint
lint: ruff-format ruff-check

# Alembic utils
.PHONY: generate
generate:
	uv run alembic revision --m="$(NAME)" --autogenerate

.PHONY: migrate
migrate:
	uv run alembic upgrade head

# Docker utils
.PHONY: project-start
project-start:
	docker-compose up --force-recreate ${MODE}

.PHONY: project-stop
project-stop:
	docker-compose down --remove-orphans ${MODE}
