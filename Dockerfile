# Separate "build" image
FROM python:3.11-slim-bullseye as compile-image
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# "Run" image
FROM python:3.11-slim-bullseye
COPY --from=compile-image /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
WORKDIR /app
COPY bot ./bot
COPY alembic.ini .
COPY alembic ./alembic
COPY Makefile .
RUN apt update && apt install -y make
CMD ["python", "-m", "bot"]