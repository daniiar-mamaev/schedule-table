FROM python:3.12.0-alpine

COPY src/ app/
COPY pyproject.toml /app
COPY poetry.lock /app

WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.create false
RUN poetry install --no-root --no-cache
RUN pip install granian
RUN rm -rf /root/.cache/pip/*

ENV PORT 80

CMD exec poetry run uvicorn project:app --host 0.0.0.0 --port $PORT