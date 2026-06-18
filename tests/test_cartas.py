"""
Suíte de testes para a API Pokémon Card Shop.

Organização:
  - Sistema       : health check
  - Listagem      : GET /cartas (vazio, paginação, filtros)
  - Criação       : POST /cartas (sucesso, defaults, payloads inválidos)
  - Busca         : GET /cartas/{id} (sucesso e 404)
  - Atualização   : PATCH /cartas/{id} (parcial, 404, payload inválido)
  - Remoção       : DELETE /cartas/{id} (sucesso, confirmação, 404)
  - Isolamento    : garante banco vazio entre execuções
"""

import pytest

# ---------------------------------------------------------------------------
# Payload base reutilizável
# ---------------------------------------------------------------------------
CARTA_BASE = {
    "nome": "Pikachu",
    "preco": 89.90,
    "estoque": 5,
    "raridade": "Rara",
    "tipo": "Elétrico",
    "expansao": "Jungle",
}


# ===========================================================================
# SISTEMA
# ===========================================================================


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["database"] == "connected"


# ===========================================================================
# LISTAGEM — GET /cartas
# ===========================================================================


def test_listar_cartas_banco_vazio(client):
    response = client.get("/cartas")
    assert response.status_code == 200
    assert response.json() == []


def test_listar_cartas_retorna_lista_nao_objeto(client, carta_existente):
    response = client.get("/cartas")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_criar_carta_aparece_na_listagem(client):
    client.post("/cartas", json=CARTA_BASE)
    response = client.get("/cartas")
    assert len(response.json()) == 1
    assert response.json()[0]["nome"] == "Pikachu"


def test_paginacao_limit(client, carta_factory):
    for i in range(5):
        carta_factory(nome=f"Carta {i}", preco=10.0 + i)

    response = client.get("/cartas", params={"limit": 2})
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_paginacao_skip(client, carta_factory):
    for i in range(5):
        carta_factory(nome=f"Carta {i}", preco=10.0 + i)

    response = client.get("/cartas", params={"skip": 4, "limit": 10})
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_filtrar_por_ativo(client, carta_factory):
    carta_factory(nome="Disponível", preco=10.0, ativo=True)
    carta_factory(nome="Indisponível", preco=10.0, ativo=False)

    ativas = client.get("/cartas", params={"ativo": True}).json()
    assert all(c["ativo"] for c in ativas)
    assert len(ativas) == 1

    inativas = client.get("/cartas", params={"ativo": False}).json()
    assert all(not c["ativo"] for c in inativas)
    assert len(inativas) == 1


def test_filtrar_por_raridade(client, carta_factory):
    carta_factory(nome="Comum", preco=5.0, raridade="Comum")
    carta_factory(nome="Ultra", preco=500.0, raridade="Ultra Rara")

    response = client.get("/cartas", params={"raridade": "Ultra Rara"})
    assert response.status_code == 200
    cartas = response.json()
    assert len(cartas) == 1
    assert cartas[0]["raridade"] == "Ultra Rara"


def test_filtrar_por_tipo(client, carta_factory):
    carta_factory(nome="Charizard", preco=100.0, tipo="Fogo")
    carta_factory(nome="Squirtle", preco=30.0, tipo="Água")

    response = client.get("/cartas", params={"tipo": "Fogo"})
    assert response.status_code == 200
    cartas = response.json()
    assert len(cartas) == 1
    assert cartas[0]["tipo"] == "Fogo"


# ===========================================================================
# CRIAÇÃO — POST /cartas
# ===========================================================================


def test_criar_carta_retorna_201_e_id(client):
    response = client.post("/cartas", json=CARTA_BASE)
    assert response.status_code == 201
    data = response.json()
    assert data["id"] is not None
    assert isinstance(data["id"], int)


def test_criar_carta_persiste_todos_os_campos(client):
    response = client.post("/cartas", json=CARTA_BASE)
    data = response.json()
    assert data["nome"] == "Pikachu"
    assert data["preco"] == 89.90
    assert data["estoque"] == 5
    assert data["raridade"] == "Rara"
    assert data["tipo"] == "Elétrico"
    assert data["expansao"] == "Jungle"


def test_criar_carta_defaults_estoque_ativo_raridade(client):
    response = client.post("/cartas", json={"nome": "Bulbasaur", "preco": 25.0})
    assert response.status_code == 201
    data = response.json()
    assert data["estoque"] == 0
    assert data["ativo"] is True
    assert data["raridade"] == "Comum"
    assert data["tipo"] is None
    assert data["expansao"] is None


def test_criar_carta_nome_e_sanitizado(client):
    """Espaços extras ao redor do nome devem ser removidos pelo validator."""
    response = client.post("/cartas", json={"nome": "  Mewtwo  ", "preco": 500.0})
    assert response.status_code == 201
    assert response.json()["nome"] == "Mewtwo"


@pytest.mark.parametrize(
    "payload,descricao",
    [
        ({"nome": "", "preco": 50.0}, "nome vazio"),
        ({"nome": "   ", "preco": 50.0}, "nome só com espaços"),
        ({"nome": "Bulbasaur", "preco": 0}, "preco zero"),
        ({"nome": "Bulbasaur", "preco": -10.0}, "preco negativo"),
        ({"nome": "Bulbasaur", "preco": 50.0, "estoque": -1}, "estoque negativo"),
        ({"preco": 50.0}, "nome ausente"),
        ({"nome": "Bulbasaur"}, "preco ausente"),
    ],
)
def test_criar_carta_payload_invalido_retorna_422(client, payload, descricao):
    response = client.post("/cartas", json=payload)
    assert response.status_code == 422, f"Esperado 422 para: {descricao}"


# ===========================================================================
# BUSCA — GET /cartas/{id}
# ===========================================================================


def test_buscar_carta_por_id_sucesso(client, carta_existente):
    carta_id = carta_existente["id"]
    response = client.get(f"/cartas/{carta_id}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Charizard"
    assert response.json()["id"] == carta_id


def test_buscar_carta_id_inexistente_retorna_404(client):
    response = client.get("/cartas/99999")
    assert response.status_code == 404


# ===========================================================================
# ATUALIZAÇÃO PARCIAL — PATCH /cartas/{id}
# ===========================================================================


def test_patch_atualiza_apenas_campo_enviado(client, carta_existente):
    carta_id = carta_existente["id"]
    response = client.patch(f"/cartas/{carta_id}", json={"preco": 999.99})
    assert response.status_code == 200
    data = response.json()
    assert data["preco"] == 999.99
    assert data["nome"] == carta_existente["nome"]  # inalterado
    assert data["estoque"] == carta_existente["estoque"]  # inalterado


def test_patch_desativar_carta(client, carta_existente):
    carta_id = carta_existente["id"]
    response = client.patch(f"/cartas/{carta_id}", json={"ativo": False})
    assert response.status_code == 200
    assert response.json()["ativo"] is False


def test_patch_carta_inexistente_retorna_404(client):
    response = client.patch("/cartas/99999", json={"preco": 100.0})
    assert response.status_code == 404


def test_patch_preco_invalido_retorna_422(client, carta_existente):
    carta_id = carta_existente["id"]
    response = client.patch(f"/cartas/{carta_id}", json={"preco": -1.0})
    assert response.status_code == 422


# ===========================================================================
# REMOÇÃO — DELETE /cartas/{id}
# ===========================================================================


def test_deletar_carta_retorna_204(client, carta_existente):
    carta_id = carta_existente["id"]
    response = client.delete(f"/cartas/{carta_id}")
    assert response.status_code == 204


def test_deletar_carta_confirma_remocao_com_get(client, carta_existente):
    carta_id = carta_existente["id"]
    client.delete(f"/cartas/{carta_id}")
    response = client.get(f"/cartas/{carta_id}")
    assert response.status_code == 404


def test_deletar_carta_inexistente_retorna_404(client):
    response = client.delete("/cartas/99999")
    assert response.status_code == 404


# ===========================================================================
# ISOLAMENTO — garante que cada teste começa com banco vazio
# ===========================================================================


def test_banco_isolado_entre_execucoes(client):
    """
    Este teste é proposital e simples: se algum estado vazasse de outro teste,
    o banco não estaria vazio aqui — o que quebraria a asserção.
    """
    response = client.get("/cartas")
    assert response.status_code == 200
    assert response.json() == [], "Banco não está vazio — isolamento da fixture client falhou"
