# Budget Tracker API

A REST API for a personal budget tracker: categories, income and expenses, monthly budgets,
a monthly summary and an import of transactions from a CSV file. Built with Python 3.13,
FastAPI and PostgreSQL.

Everything runs in Docker, so only **Docker Desktop** is needed. Run all commands from the
project root.

## Run the app

```bash
docker compose up -d --build
```

This starts the database and the API. The API runs at <http://localhost:8000>. The data is
kept in a Docker volume, so it is still there after a restart. `docker compose down` stops the
app; `docker compose down -v` also deletes the data.

If another PostgreSQL already uses port 5432 on your computer, copy `.env.example` to `.env`
and set another port there, e.g. 5433.

## API documentation

While the app runs, every endpoint with its input and output is documented at:

- <http://localhost:8000/docs>: Swagger UI, where every endpoint can also be tried out
- <http://localhost:8000/redoc>
- <http://localhost:8000/openapi.json>: the OpenAPI specification

## Run the tests

While the app runs:

```bash
docker compose exec api pytest
```

The tests use their own database (`budget_tracker_test`), so the app's data is never touched.

## Test data (the data command)

While the app runs:

```bash
docker compose exec api python -m app.seed
```

It adds categories, budgets and transactions for the current month and the two months before
it. `--expenses N` sets the number of random expenses (default 150). An example CSV file for
the import is [`csv/transactions.csv`](csv/transactions.csv); it uses the categories
"Eating out" and "Other", which must exist first.

## Without Docker (optional)

With Python 3.13, and the database still in Docker:

```bash
docker compose up -d db
pip install -r requirements.txt
fastapi dev
```

Then `pytest` runs the tests and `python -m app.seed` adds the test data.
