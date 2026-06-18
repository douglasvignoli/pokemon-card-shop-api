import os
from enum import Enum
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Boolean, Column, Float, Integer, String, create_engine, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker


# ---------------------------------------------------------------------------
# Configuração — lida de variável de ambiente via Pydantic Settings.
# Mais robusto que os.getenv: valida tipo, suporta .env e falha rápido se
# a variável obrigatória estiver ausente.
# ---------------------------------------------------------------------------
class Settings(BaseSettings):
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/pokemon_db",
    )

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

# ---------------------------------------------------------------------------
# Banco de dados
# ---------------------------------------------------------------------------
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Enums de domínio — expansão além do enunciado.
# Cartas Pokémon possuem raridade e tipo bem definidos; modelar isso como Enum
# garante integridade no banco e validação automática pelo Pydantic/FastAPI.
# ---------------------------------------------------------------------------
class Raridade(str, Enum):
    comum = "Comum"
    incomum = "Incomum"
    rara = "Rara"
    holo_rara = "Holo Rara"
    ultra_rara = "Ultra Rara"
    secreta = "Secreta"


class Tipo(str, Enum):
    fogo = "Fogo"
    agua = "Água"
    grama = "Grama"
    eletrico = "Elétrico"
    psiquico = "Psíquico"
    lutador = "Lutador"
    sombrio = "Sombrio"
    metal = "Metal"
    dragao = "Dragão"
    incolor = "Incolor"


# ---------------------------------------------------------------------------
# Modelo SQLAlchemy
# ---------------------------------------------------------------------------
class Carta(Base):
    __tablename__ = "cartas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    preco = Column(Float, nullable=False)
    estoque = Column(Integer, default=0, nullable=False)
    ativo = Column(Boolean, default=True, nullable=False)
    raridade = Column(String, default=Raridade.comum, nullable=False)
    tipo = Column(String, nullable=True)
    expansao = Column(String, nullable=True)


# ---------------------------------------------------------------------------
# Schemas Pydantic
# Separar CartaCreate (entrada) de CartaResponse (saída) é boas práticas:
# evita expor campos internos e permite evoluir os contratos de forma independente.
# ---------------------------------------------------------------------------
class CartaCreate(BaseModel):
    nome: str
    preco: float
    estoque: int = 0
    ativo: bool = True
    raridade: Raridade = Raridade.comum
    tipo: Optional[Tipo] = None
    expansao: Optional[str] = None

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("nome não pode ser vazio ou conter apenas espaços")
        return v.strip()

    @field_validator("preco")
    @classmethod
    def preco_deve_ser_positivo(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("preco deve ser maior que zero")
        return v

    @field_validator("estoque")
    @classmethod
    def estoque_nao_pode_ser_negativo(cls, v: int) -> int:
        if v < 0:
            raise ValueError("estoque não pode ser negativo")
        return v


class CartaUpdate(BaseModel):
    """Schema para atualização parcial (PATCH) — todos os campos são opcionais."""

    nome: Optional[str] = None
    preco: Optional[float] = None
    estoque: Optional[int] = None
    ativo: Optional[bool] = None
    raridade: Optional[Raridade] = None
    tipo: Optional[Tipo] = None
    expansao: Optional[str] = None

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("nome não pode ser vazio ou conter apenas espaços")
        return v.strip() if v else v

    @field_validator("preco")
    @classmethod
    def preco_deve_ser_positivo(cls, v: Optional[float]) -> Optional[float]:
        if v is not None and v <= 0:
            raise ValueError("preco deve ser maior que zero")
        return v

    @field_validator("estoque")
    @classmethod
    def estoque_nao_pode_ser_negativo(cls, v: Optional[int]) -> Optional[int]:
        if v is not None and v < 0:
            raise ValueError("estoque não pode ser negativo")
        return v


class CartaResponse(BaseModel):
    id: int
    nome: str
    preco: float
    estoque: int
    ativo: bool
    raridade: Raridade
    tipo: Optional[Tipo]
    expansao: Optional[str]

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Dependency Injection
# ---------------------------------------------------------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------
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


# ---------------------------------------------------------------------------
# Endpoints de sistema
# ---------------------------------------------------------------------------
@app.get("/health", tags=["Sistema"], summary="Verifica saúde da API e do banco")
def health_check(db: Session = Depends(get_db)):
    """
    Retorna status da API e conectividade com o banco de dados.
    Útil para liveness/readiness probes em ambientes de container.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception:
        raise HTTPException(status_code=503, detail="Banco de dados indisponível")


# ---------------------------------------------------------------------------
# Endpoints de cartas
# ---------------------------------------------------------------------------
@app.get(
    "/cartas",
    response_model=list[CartaResponse],
    tags=["Cartas"],
    summary="Lista cartas com filtros e paginação",
)
def listar_cartas(
    ativo: Optional[bool] = Query(None, description="Filtrar por disponibilidade"),
    raridade: Optional[Raridade] = Query(None, description="Filtrar por raridade"),
    tipo: Optional[Tipo] = Query(None, description="Filtrar por tipo de carta"),
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros retornados"),
    db: Session = Depends(get_db),
):
    query = db.query(Carta)
    if ativo is not None:
        query = query.filter(Carta.ativo == ativo)
    if raridade is not None:
        query = query.filter(Carta.raridade == raridade.value)
    if tipo is not None:
        query = query.filter(Carta.tipo == tipo.value)
    return query.offset(skip).limit(limit).all()


@app.post(
    "/cartas",
    response_model=CartaResponse,
    status_code=201,
    tags=["Cartas"],
    summary="Cadastra uma nova carta",
)
def criar_carta(carta: CartaCreate, db: Session = Depends(get_db)):
    db_carta = Carta(**carta.model_dump())
    db.add(db_carta)
    db.commit()
    db.refresh(db_carta)
    return db_carta


@app.get(
    "/cartas/{id}",
    response_model=CartaResponse,
    tags=["Cartas"],
    summary="Busca carta por ID",
)
def buscar_carta(id: int, db: Session = Depends(get_db)):
    carta = db.query(Carta).filter(Carta.id == id).first()
    if not carta:
        raise HTTPException(status_code=404, detail=f"Carta com id {id} não encontrada")
    return carta


@app.patch(
    "/cartas/{id}",
    response_model=CartaResponse,
    tags=["Cartas"],
    summary="Atualiza campos específicos de uma carta",
)
def atualizar_carta(id: int, dados: CartaUpdate, db: Session = Depends(get_db)):
    """
    Atualização parcial via PATCH: apenas os campos enviados são alterados.
    Utiliza model_dump(exclude_unset=True) para ignorar campos não informados.
    """
    carta = db.query(Carta).filter(Carta.id == id).first()
    if not carta:
        raise HTTPException(status_code=404, detail=f"Carta com id {id} não encontrada")
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(carta, campo, valor)
    db.commit()
    db.refresh(carta)
    return carta


@app.delete(
    "/cartas/{id}",
    status_code=204,
    tags=["Cartas"],
    summary="Remove uma carta do catálogo",
)
def deletar_carta(id: int, db: Session = Depends(get_db)):
    carta = db.query(Carta).filter(Carta.id == id).first()
    if not carta:
        raise HTTPException(status_code=404, detail=f"Carta com id {id} não encontrada")
    db.delete(carta)
    db.commit()
