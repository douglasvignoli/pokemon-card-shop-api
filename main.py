from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import cartas, health

app = FastAPI(
    title="Pokémon Card Shop API",
    description=(
        "API REST para gerenciamento de cartas Pokémon. "
        "Permite cadastrar, listar, buscar, atualizar e remover cartas do catálogo."
    ),
    version="1.0.0",
    contact={"name": "Pokémon Card Shop", "email": "contato@pokemonshop.com"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(cartas.router)
