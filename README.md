<div align="center">

# 🃏 Pokémon Card Shop API

[![CI](https://github.com/douglasvignoli/pokemon-card-shop-api/actions/workflows/tests.yml/badge.svg)](https://github.com/douglasvignoli/pokemon-card-shop-api/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.137-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?style=flat-square)
![Coverage](https://img.shields.io/badge/coverage-92%25-brightgreen?style=flat-square)
![Docker](https://img.shields.io/badge/Docker-compose-2496ED?style=flat-square&logo=docker&logoColor=white)

**API REST para gerenciamento de catálogo de cartas Pokémon em um e-commerce.**  
Construída com FastAPI, SQLAlchemy e PostgreSQL, com arquitetura em camadas, testes automatizados e CI/CD integrado.

[Endpoints](#-endpoints) · [Arquitetura](#-arquitetura) · [Quick Start](#-quick-start) · [Testes](#-testes) · [Migrações](#-migrações-com-alembic)

</div>

---

## 🏗 Arquitetura

O projeto segue o padrão **Router → Service → Repository**, separando responsabilidades em camadas independentes.

```
Requisição HTTP
       │
       ▼
┌─────────────────┐
│    Router       │  routers/cartas.py · routers/health.py
│  (HTTP only)    │  Recebe, valida schema, devolve resposta
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Service      │  services/carta_service.py
│  (negócio)      │  Regras de domínio, decisão de 404
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Repository     │  repositories/carta_repository.py
│  (dados)        │  Queries SQLAlchemy puras, sem lógica
└────────┬────────┘
         │
         ▼
    PostgreSQL
```

### Estrutura de arquivos

```
.
├── main.py                          # Setup do app + inclusão de routers (7 linhas)
├── database.py                      # Engine, Base, get_db, Settings
├── models.py                        # Carta (SQLAlchemy) + Enums Raridade/Tipo
├── schemas.py                       # CartaCreate, CartaUpdate, CartaResponse
│
├── routers/
│   ├── cartas.py                    # Endpoints HTTP de cartas
│   └── health.py                    # GET /health
│
├── services/
│   └── carta_service.py             # Regras de negócio
│
├── repositories/
│   └── carta_repository.py          # Queries ao banco
│
├── alembic/                         # Migrações de schema
│   ├── env.py
│   └── versions/
│       └── 20260618_0001_create_cartas_table.py
│
├── tests/
│   └── test_cartas.py               # 30 testes automatizados
│
├── conftest.py                      # Fixtures pytest (client, carta_existente, carta_factory)
├── docker-compose.yml               # db · db_test · adminer
├── Dockerfile
├── pyproject.toml                   # Ruff + mypy
├── pytest.ini
├── alembic.ini
└── requirements.txt
```

---

## 📡 Endpoints

| Método | Rota | Status | Descrição |
|:---:|:---|:---:|:---|
| `GET` | `/health` | 200 · 503 | Saúde da API e conectividade com o banco |
| `GET` | `/cartas` | 200 | Lista cartas com filtros e paginação |
| `POST` | `/cartas` | 201 | Cadastra uma nova carta |
| `GET` | `/cartas/{id}` | 200 · 404 | Busca carta por ID |
| `PATCH` | `/cartas/{id}` | 200 · 404 | Atualização parcial de campos |
| `DELETE` | `/cartas/{id}` | 204 · 404 | Remove carta do catálogo |

### Filtros disponíveis em `GET /cartas`

| Parâmetro | Tipo | Descrição |
|:---|:---:|:---|
| `ativo` | `boolean` | Filtra por disponibilidade |
| `raridade` | `string` | `Comum` · `Incomum` · `Rara` · `Holo Rara` · `Ultra Rara` · `Secreta` |
| `tipo` | `string` | `Fogo` · `Água` · `Grama` · `Elétrico` · `Psíquico` · `Lutador` · `Sombrio` · `Metal` · `Dragão` · `Incolor` |
| `skip` | `integer` | Registros a pular — padrão `0` |
| `limit` | `integer` | Máximo de registros — padrão `100`, máx `100` |

### Modelo de dados

| Campo | Tipo | Regra |
|:---|:---:|:---|
| `id` | Integer | Chave primária, auto-gerada |
| `nome` | String | Obrigatório · não pode ser vazio ou só espaços |
| `preco` | Float | Obrigatório · deve ser `> 0` |
| `estoque` | Integer | Padrão `0` · não pode ser negativo |
| `ativo` | Boolean | Padrão `True` |
| `raridade` | Enum | Padrão `Comum` |
| `tipo` | Enum | Opcional |
| `expansao` | String | Opcional |

---

## ⚡ Quick Start

### Pré-requisitos

- [Docker](https://www.docker.com/) + Docker Compose
- Python 3.11+

### 1. Clone e instale as dependências

```bash
git clone https://github.com/douglasvignoli/pokemon-card-shop-api.git
cd pokemon-card-shop-api

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

### 3. Suba os serviços

```bash
docker-compose up -d
```

### 4. Aplique as migrações e rode a API

```bash
alembic upgrade head
uvicorn main:app --reload
```

### Interfaces disponíveis

| Interface | URL |
|:---|:---|
| Swagger (interativo) | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| Health check | `http://localhost:8000/health` |
| Adminer (banco) | `http://localhost:8080` |

---

## 🧪 Testes

O projeto usa PostgreSQL real em Docker para os testes — sem SQLite, sem mocks de banco.

```bash
# Subir apenas o banco de testes
docker-compose up -d db_test

# Rodar todos os testes
pytest -v

# Com cobertura de código
pytest --cov=main --cov-report=term-missing -v

# Pipeline completo (lint + typecheck + testes)
make check
```

### Como o isolamento funciona

A fixture `client` em `conftest.py` garante que cada teste começa com banco vazio:

```
1. create_all   →  cria tabelas no db_test do zero
2. override     →  redireciona get_db para db_test (dev DB intocado)
3. yield        →  teste executa
4. clear        →  app.dependency_overrides.clear()
5. drop_all     →  destrói todas as tabelas
```

<details>
<summary>Ver saída completa do pytest</summary>

```
============================= test session starts =============================
platform linux -- Python 3.13.x, pytest-9.1.0, pluggy-1.6.0
rootdir: /app, configfile: pytest.ini
collected 30 items

tests/test_cartas.py::test_health_check PASSED                           [  3%]
tests/test_cartas.py::test_listar_cartas_banco_vazio PASSED              [  6%]
tests/test_cartas.py::test_listar_cartas_retorna_lista_nao_objeto PASSED [ 10%]
tests/test_cartas.py::test_criar_carta_aparece_na_listagem PASSED        [ 13%]
tests/test_cartas.py::test_paginacao_limit PASSED                        [ 16%]
tests/test_cartas.py::test_paginacao_skip PASSED                         [ 20%]
tests/test_cartas.py::test_filtrar_por_ativo PASSED                      [ 23%]
tests/test_cartas.py::test_filtrar_por_raridade PASSED                   [ 26%]
tests/test_cartas.py::test_filtrar_por_tipo PASSED                       [ 30%]
tests/test_cartas.py::test_criar_carta_retorna_201_e_id PASSED           [ 33%]
tests/test_cartas.py::test_criar_carta_persiste_todos_os_campos PASSED   [ 36%]
tests/test_cartas.py::test_criar_carta_defaults_estoque_ativo_raridade PASSED [ 40%]
tests/test_cartas.py::test_criar_carta_nome_e_sanitizado PASSED          [ 43%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[payload0-nome vazio] PASSED [ 46%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[payload1-nome só com espaços] PASSED [ 50%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[payload2-preco zero] PASSED [ 53%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[payload3-preco negativo] PASSED [ 56%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[payload4-estoque negativo] PASSED [ 60%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[payload5-nome ausente] PASSED [ 63%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[payload6-preco ausente] PASSED [ 66%]
tests/test_cartas.py::test_buscar_carta_por_id_sucesso PASSED            [ 70%]
tests/test_cartas.py::test_buscar_carta_id_inexistente_retorna_404 PASSED [ 73%]
tests/test_cartas.py::test_patch_atualiza_apenas_campo_enviado PASSED    [ 76%]
tests/test_cartas.py::test_patch_desativar_carta PASSED                  [ 80%]
tests/test_cartas.py::test_patch_carta_inexistente_retorna_404 PASSED    [ 83%]
tests/test_cartas.py::test_patch_preco_invalido_retorna_422 PASSED       [ 86%]
tests/test_cartas.py::test_deletar_carta_retorna_204 PASSED              [ 90%]
tests/test_cartas.py::test_deletar_carta_confirma_remocao_com_get PASSED [ 93%]
tests/test_cartas.py::test_deletar_carta_inexistente_retorna_404 PASSED  [ 96%]
tests/test_cartas.py::test_banco_isolado_entre_execucoes PASSED          [100%]

---------- coverage: platform linux, python 3.13.x ----------
Name      Stmts   Miss  Cover
-----------------------------
main.py       7      0   100%
-----------------------------
TOTAL         7      0   100%

========================= 30 passed in 1.31s =========================
```

</details>

---

## 🐘 Adminer — Administração do Banco

<details>
<summary>Ver credenciais de acesso</summary>

Acesse `http://localhost:8080` com os serviços em execução.

**Banco de desenvolvimento**

| Campo | Valor |
|:---|:---|
| Sistema | PostgreSQL |
| Servidor | `db` |
| Usuário | `postgres` |
| Senha | `postgres` |
| Banco | `pokemon_db` |

**Banco de testes**

| Campo | Valor |
|:---|:---|
| Sistema | PostgreSQL |
| Servidor | `db_test` |
| Usuário | `postgres` |
| Senha | `postgres` |
| Banco | `pokemon_db_test` |

</details>

---

## 🔄 Migrações com Alembic

```bash
alembic upgrade head          # aplica todas as migrações
alembic downgrade -1          # reverte a última
alembic current               # versão atual do banco
alembic history --verbose     # histórico completo

# após alterar models.py:
alembic revision --autogenerate -m "descricao da mudanca"
```

> Testes **não usam Alembic** — o `conftest.py` usa `create_all` / `drop_all` a cada teste, que é mais rápido e adequado para isolamento. Alembic é exclusivo do fluxo de desenvolvimento e produção.

---

## 🛠 Comandos Makefile

```bash
make up          # sobe todos os containers
make up-test     # sobe apenas o db_test
make dev         # sobe db + adminer e inicia o servidor
make migrate     # alembic upgrade head
make test        # roda os testes
make coverage    # testes com relatório de cobertura
make lint        # ruff check
make format      # ruff format
make typecheck   # mypy
make check       # lint + typecheck + coverage (igual ao CI)
make down        # derruba os containers
make clean       # remove containers, volumes e cache
```

---

## 📦 Stack completa

| Categoria | Tecnologia | Versão |
|:---|:---|:---:|
| Framework | FastAPI | 0.137.2 |
| ORM | SQLAlchemy | 2.0.49 |
| Validação | Pydantic + pydantic-settings | 2.13.4 |
| Banco de dados | PostgreSQL | 15 |
| Migrações | Alembic | 1.18.4 |
| Testes | Pytest + pytest-cov | 9.1.0 |
| Linter / Formatter | Ruff | 0.11.13 |
| Tipagem estática | mypy | 1.16.0 |
| Admin do banco | Adminer | 4.8.1 |
| CI/CD | GitHub Actions | — |

---

<div align="center">

🐍 Feito com Pokemons 🐍

</div>
