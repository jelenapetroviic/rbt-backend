from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, sessionmaker

from app.config import settings
from app.dependencies import get_db
from app.main import app
from app.models import Base

app_url = make_url(settings.database_url)
test_url = app_url.set(database=f"{app_url.database}_test")
engine = create_engine(test_url)
TestSession = sessionmaker(bind=engine, expire_on_commit=False)


def get_test_db() -> Iterator[Session]:
    with TestSession() as session:
        yield session


@pytest.fixture(scope="session", autouse=True)
def create_test_database() -> None:
    server = create_engine(test_url.set(database="postgres"), isolation_level="AUTOCOMMIT")
    with server.connect() as connection:
        query = text("SELECT 1 FROM pg_database WHERE datname = :name")
        if not connection.scalar(query, {"name": test_url.database}):
            connection.execute(text(f'CREATE DATABASE "{test_url.database}"'))
    server.dispose()


@pytest.fixture
def client() -> Iterator[TestClient]:
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    app.dependency_overrides[get_db] = get_test_db
    yield TestClient(app)
    app.dependency_overrides.clear()
