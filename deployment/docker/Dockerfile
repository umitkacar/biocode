FROM python:3.11-slim as builder

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --no-dev

FROM python:3.11-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/
COPY config/ ./config/

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src:$PYTHONPATH"

EXPOSE 8000 9090

CMD ["python", "-m", "biocode.interfaces.api"]
