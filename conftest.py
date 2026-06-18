import os
from typing import Callable

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import Base, app, get_db

TEST_DATABASE_URL = os.getenv(
    "TEST_DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5433/pokemon_db_test",
)

test_engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


# ---------------------------------------------------------------------------
# Fixture principal — garante isolamento completo entre testes.
#
# Ciclo por teste:
#   1. create_all  → cria tabelas no banco de testes do zero
#   2. dependency_overrides → redireciona get_db para o banco de testes
#   3. yield TestClient → executa o teste
#   4. clear overrides → restaura dependências originais
#   5. drop_all → destrói todas as tabelas, limpando qualquer estado
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Fixture auxiliar — cria uma carta real no banco antes do teste.
# Depende de `client` para garantir que roda dentro do ciclo de isolamento.
# ---------------------------------------------------------------------------
@pytest.fixture()
def carta_existente(client: TestClient) -> dict:
    response = client.post("/cartas", json={
        "nome": "Charizard",
        "preco": 250.00,
        "estoque": 3,
        "raridade": "Holo Rara",
        "tipo": "Fogo",
        "expansao": "Base Set",
    })
    assert response.status_code == 201
    return response.json()


# ---------------------------------------------------------------------------
# Fixture de fábrica — padrão avançado que retorna uma função para criar
# cartas com parâmetros customizados. Evita duplicação nos testes que
# precisam de múltiplos registros com atributos variados.
# ---------------------------------------------------------------------------
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
