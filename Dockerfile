FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY pyproject.toml .
COPY app ./app
COPY tests ./tests

RUN useradd --system app
USER app

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--port", "8000"]
