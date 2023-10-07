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

.PHONY:	black
black:
	poetry run black src/

.PHONY:	mypy
mypy:
	poetry run mypy --strict --pretty --explicit-package-bases --install-types src/

.PHONY: ruff
ruff:
	poetry run ruff check src/ --fix --respect-gitignore

.PHONY: lint
lint: black ruff

.PHONY: run
run:
	migrate
	poetry run python -m src.bot

# Poetry and environments utils
REQUIREMENTS_FILE := requirements.txt

.PHONY: requirements
requirements:
	# Export poetry.lock to requirements.txt if needed
	poetry check
	poetry export -o ${REQUIREMENTS_FILE} --without-hashes


# Alembic utils
.PHONY: generate
generate:
	poetry run alembic revision --m="$(NAME)" --autogenerate

.PHONY: migrate
migrate:
	poetry run alembic upgrade head

# Docker utils
.PHONY: project-start
project-start:
	docker-compose up --force-recreate ${MODE}

.PHONY: project-stop
project-stop:
	docker-compose down --remove-orphans ${MODE}
