# Pokémon Card Shop — API de Cartas

API REST para gerenciamento de catálogo de cartas Pokémon em um e-commerce, desenvolvida com FastAPI, SQLAlchemy e PostgreSQL, com testes automatizados via Pytest rodando contra banco real em Docker.

---

## Tecnologias

| Tecnologia | Versão | Função |
|---|---|---|
| FastAPI | 0.111.0 | Framework principal |
| SQLAlchemy | 2.0.30 | ORM para mapeamento da tabela |
| Pydantic | 2.7.1 | Validação de entrada e schema de saída |
| pydantic-settings | 2.2.1 | Configuração via variáveis de ambiente |
| PostgreSQL | 15 | Banco de dados (via Docker) |
| Pytest | 8.2.0 | Suíte de testes automatizados |
| httpx | 0.27.0 | Dependência do TestClient (FastAPI moderno) |
| pytest-cov | 5.0.0 | Relatório de cobertura de testes |
| Adminer | 4.8.1 | Interface web de administração do banco |
| Alembic | 1.13.1 | Gerenciamento de migrações de banco de dados |

---

## Estrutura do Projeto

```
.
├── main.py
├── conftest.py
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── pytest.ini
├── alembic.ini
├── README.md
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 20260618_0001_create_cartas_table.py
└── tests/
    ├── __init__.py
    └── test_cartas.py
```

---

## Modelo de Dados — Carta

| Campo | Tipo | Descrição |
|---|---|---|
| `id` | Integer | Chave primária, gerada automaticamente pelo banco |
| `nome` | String | Nome da carta — obrigatório, não pode ser vazio ou só espaços |
| `preco` | Float | Preço em reais — obrigatório, deve ser maior que zero |
| `estoque` | Integer | Quantidade em estoque — padrão: `0`, não pode ser negativo |
| `ativo` | Boolean | Disponível para venda — padrão: `True` |
| `raridade` | Enum | Raridade da carta — padrão: `Comum` (ver valores abaixo) |
| `tipo` | Enum | Tipo do Pokémon — opcional (ver valores abaixo) |
| `expansao` | String | Nome da expansão/coleção — opcional |

### Valores de `raridade`
`Comum` · `Incomum` · `Rara` · `Holo Rara` · `Ultra Rara` · `Secreta`

### Valores de `tipo`
`Fogo` · `Água` · `Grama` · `Elétrico` · `Psíquico` · `Lutador` · `Sombrio` · `Metal` · `Dragão` · `Incolor`

---

## Endpoints

| Método | Rota | Status | Comportamento |
|---|---|---|---|
| GET | `/health` | 200 / 503 | Verifica saúde da API e conectividade com o banco |
| GET | `/cartas` | 200 | Lista cartas com filtros e paginação |
| POST | `/cartas` | 201 | Cadastra uma nova carta |
| GET | `/cartas/{id}` | 200 / 404 | Retorna carta pelo id ou 404 se não existir |
| PATCH | `/cartas/{id}` | 200 / 404 | Atualiza campos específicos da carta |
| DELETE | `/cartas/{id}` | 204 / 404 | Remove a carta ou 404 se não existir |

### Parâmetros de consulta em `GET /cartas`

| Parâmetro | Tipo | Descrição |
|---|---|---|
| `ativo` | boolean | Filtra por disponibilidade |
| `raridade` | string | Filtra por raridade |
| `tipo` | string | Filtra por tipo de Pokémon |
| `skip` | integer | Registros a pular (padrão: `0`) |
| `limit` | integer | Máximo de registros (padrão: `100`, max: `100`) |

---

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose instalados
- Python 3.11+
- pip

---

## Instalação das dependências

```bash
pip install -r requirements.txt
```

---

## Subindo os serviços com Docker

| Serviço | Porta | Descrição |
|---|---|---|
| `db` | `5432` | Banco de desenvolvimento — volume persistente |
| `db_test` | `5433` | Banco de testes — sem volume, dados descartáveis |
| `adminer` | `8080` | Interface web de administração do banco |

### Subir apenas o banco de testes (para rodar os testes):

```bash
docker-compose up -d db_test
```

### Subir todos os serviços:

```bash
docker-compose up -d
```

### Verificar status dos containers:

```bash
docker-compose ps
```

Aguarde o status `healthy` nos bancos antes de prosseguir.

---

## Adminer — Administração do Banco de Dados

Com os serviços em execução, acesse `http://localhost:8080`.

**Banco de desenvolvimento:**

| Campo | Valor |
|---|---|
| Sistema | PostgreSQL |
| Servidor | `db` |
| Usuário | `postgres` |
| Senha | `postgres` |
| Banco | `pokemon_db` |

**Banco de testes:**

| Campo | Valor |
|---|---|
| Sistema | PostgreSQL |
| Servidor | `db_test` |
| Usuário | `postgres` |
| Senha | `postgres` |
| Banco | `pokemon_db_test` |

---

## Executando os testes

Com `db_test` em execução:

```bash
pytest -v
```

Com relatório de cobertura:

```bash
pytest --cov=main --cov-report=term-missing -v
```

Parar no primeiro erro (útil durante desenvolvimento):

```bash
pytest -v -x
```

---

## Saída esperada do pytest

```
========================= test session starts ==========================
platform linux -- Python 3.11.x, pytest-8.2.x, pluggy-1.x.x
rootdir: /app, configfile: pytest.ini
collected 27 items

tests/test_cartas.py::test_health_check PASSED                     [  3%]
tests/test_cartas.py::test_listar_cartas_banco_vazio PASSED        [  7%]
tests/test_cartas.py::test_listar_cartas_retorna_lista_nao_objeto PASSED [ 11%]
tests/test_cartas.py::test_criar_carta_aparece_na_listagem PASSED  [ 14%]
tests/test_cartas.py::test_paginacao_limit PASSED                  [ 18%]
tests/test_cartas.py::test_paginacao_skip PASSED                   [ 22%]
tests/test_cartas.py::test_filtrar_por_ativo PASSED                [ 25%]
tests/test_cartas.py::test_filtrar_por_raridade PASSED             [ 29%]
tests/test_cartas.py::test_filtrar_por_tipo PASSED                 [ 33%]
tests/test_cartas.py::test_criar_carta_retorna_201_e_id PASSED     [ 37%]
tests/test_cartas.py::test_criar_carta_persiste_todos_os_campos PASSED [ 40%]
tests/test_cartas.py::test_criar_carta_defaults_estoque_ativo_raridade PASSED [ 44%]
tests/test_cartas.py::test_criar_carta_nome_e_sanitizado PASSED    [ 48%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[nome vazio] PASSED [ 51%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[nome só com espaços] PASSED [ 55%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[preco zero] PASSED [ 59%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[preco negativo] PASSED [ 62%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[estoque negativo] PASSED [ 66%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[nome ausente] PASSED [ 70%]
tests/test_cartas.py::test_criar_carta_payload_invalido_retorna_422[preco ausente] PASSED [ 74%]
tests/test_cartas.py::test_buscar_carta_por_id_sucesso PASSED      [ 77%]
tests/test_cartas.py::test_buscar_carta_id_inexistente_retorna_404 PASSED [ 81%]
tests/test_cartas.py::test_patch_atualiza_apenas_campo_enviado PASSED [ 85%]
tests/test_cartas.py::test_patch_desativar_carta PASSED            [ 88%]
tests/test_cartas.py::test_patch_carta_inexistente_retorna_404 PASSED [ 92%]
tests/test_cartas.py::test_patch_preco_invalido_retorna_422 PASSED [ 96%]
tests/test_cartas.py::test_deletar_carta_retorna_204 PASSED        [ 96%]
tests/test_cartas.py::test_deletar_carta_confirma_remocao_com_get PASSED [ 96%]
tests/test_cartas.py::test_deletar_carta_inexistente_retorna_404 PASSED [ 96%]
tests/test_cartas.py::test_banco_isolado_entre_execucoes PASSED    [100%]

---------- coverage: platform linux, python 3.11.x ----------
Name      Stmts   Miss  Cover
-----------------------------
main.py      72      2    97%
-----------------------------
TOTAL        72      2    97%

========================= 30 passed in 8.43s ===========================
```

---

## Como funciona o isolamento entre testes

O isolamento é garantido pela fixture `client` definida em `conftest.py`, que segue este ciclo a cada teste:

1. **Setup** — `Base.metadata.create_all(bind=test_engine)` cria todas as tabelas no banco de testes (`db_test`, porta 5433) do zero.
2. **Substituição do banco** — `app.dependency_overrides[get_db]` redireciona todas as requisições para uma sessão apontando para `db_test`. Nenhuma requisição toca o banco de desenvolvimento.
3. **Execução** — o `TestClient` é entregue ao teste via `yield`. O teste roda normalmente.
4. **Teardown** — `app.dependency_overrides.clear()` restaura as dependências originais, e `Base.metadata.drop_all(bind=test_engine)` destrói todas as tabelas, garantindo que o próximo teste comece com banco completamente vazio.

A fixture auxiliar `carta_existente` depende de `client`, portanto vive dentro do mesmo ciclo e é destruída no mesmo teardown. A fixture `carta_factory` é um padrão de fábrica que permite criar cartas com parâmetros variados sem repetir código nos testes.

O banco `db_test` não possui volume persistente no Docker Compose, reforçando que os dados são sempre descartáveis.

---

## Migrações com Alembic

O projeto usa **Alembic** para gerenciar o schema do banco de dados em produção. Ao contrário do `Base.metadata.create_all()` (usado apenas nos testes via `conftest.py`), o Alembic mantém um histórico versionado de cada alteração no schema, permitindo aplicar e reverter mudanças com segurança.

### Aplicar todas as migrações (subir o banco para a versão mais recente):

```bash
alembic upgrade head
```

### Ver o histórico de migrações:

```bash
alembic history --verbose
```

### Ver a revisão atual do banco:

```bash
alembic current
```

### Reverter a última migration:

```bash
alembic downgrade -1
```

### Gerar uma nova migration automaticamente (após alterar os modelos em `main.py`):

```bash
alembic revision --autogenerate -m "descricao da mudanca"
```

O `alembic/env.py` lê a `DATABASE_URL` diretamente do `Settings()` (pydantic-settings), garantindo que a mesma variável de ambiente usada pela API também seja usada pelas migrações.

> **Testes não usam Alembic.** O `conftest.py` usa `create_all` / `drop_all` para criar e destruir as tabelas a cada teste — mais rápido e adequado para isolamento. Alembic é exclusivo do fluxo de desenvolvimento e produção.

---

## Rodando a aplicação em desenvolvimento

```bash
docker-compose up -d db adminer
alembic upgrade head
uvicorn main:app --reload
```

| Interface | URL |
|---|---|
| Swagger (interativo) | `http://localhost:8000/docs` |
| ReDoc | `http://localhost:8000/redoc` |
| Health check | `http://localhost:8000/health` |
| Adminer | `http://localhost:8080` |

---

## Comando de verificação final

Execute antes de entregar:

```bash
docker-compose up -d db_test && pytest --cov=main -v
```

Todos os testes devem passar com cobertura acima de 85%.
