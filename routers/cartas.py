from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Raridade, Tipo
from schemas import CartaCreate, CartaResponse, CartaUpdate
from services.carta_service import carta_service

router = APIRouter(prefix="/cartas", tags=["Cartas"])


@router.get("", response_model=list[CartaResponse], summary="Lista cartas com filtros e paginação")
def listar_cartas(
    ativo: bool | None = Query(None, description="Filtrar por disponibilidade"),
    raridade: Raridade | None = Query(None, description="Filtrar por raridade"),
    tipo: Tipo | None = Query(None, description="Filtrar por tipo de carta"),
    skip: int = Query(0, ge=0, description="Registros a pular (paginação)"),
    limit: int = Query(100, ge=1, le=100, description="Máximo de registros retornados"),
    db: Session = Depends(get_db),
) -> list:
    return carta_service.listar_cartas(
        db, ativo=ativo, raridade=raridade, tipo=tipo, skip=skip, limit=limit
    )


@router.post("", response_model=CartaResponse, status_code=201, summary="Cadastra uma nova carta")
def criar_carta(carta: CartaCreate, db: Session = Depends(get_db)):
    return carta_service.criar_carta(db, carta)


@router.get("/{id}", response_model=CartaResponse, summary="Busca carta por ID")
def buscar_carta(id: int, db: Session = Depends(get_db)):
    return carta_service.buscar_carta(db, id)


@router.patch(
    "/{id}", response_model=CartaResponse, summary="Atualiza campos específicos de uma carta"
)
def atualizar_carta(id: int, dados: CartaUpdate, db: Session = Depends(get_db)):
    return carta_service.atualizar_carta(db, id, dados)


@router.delete("/{id}", status_code=204, summary="Remove uma carta do catálogo")
def deletar_carta(id: int, db: Session = Depends(get_db)) -> None:
    carta_service.deletar_carta(db, id)
