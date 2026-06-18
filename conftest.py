import os
from collections.abc import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database import Base, get_db
from main import app

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/pokemon_db_test",
)

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture()
def client() -> TestClient:
    Base.metadata.create_all(bind=test_engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def carta_existente(client: TestClient) -> dict:
    response = client.post(
        "/cartas",
        json={
            "nome": "Charizard",
            "preco": 250.00,
            "estoque": 3,
            "raridade": "Holo Rara",
            "tipo": "Fogo",
            "expansao": "Base Set",
        },
    )
    assert response.status_code == 201
    return response.json()


@pytest.fixture()
def carta_factory(client: TestClient) -> Callable:
    def _criar(**kwargs) -> dict:
        payload = {
            "nome": "Pikachu",
            "preco": 50.0,
            "estoque": 10,
            **kwargs,
        }
        response = client.post("/cartas", json=payload)
        assert response.status_code == 201, (
            f"carta_factory falhou ao criar carta: {response.json()}"
        )
        return response.json()

    return _criar
