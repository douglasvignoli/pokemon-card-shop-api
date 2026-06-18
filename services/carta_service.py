from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Carta, Raridade, Tipo
from repositories.carta_repository import CartaRepository, carta_repository
from schemas import CartaCreate, CartaUpdate


class CartaService:
    """Camada de negócio — orquestra repositório e aplica regras da aplicação.

    O service é o único lugar onde HTTPException é lançado: a decisão de que
    'carta não encontrada = 404' é uma regra de negócio, não de infraestrutura.
    O repositório apenas retorna None; quem decide o que fazer com isso é aqui.
    """

    def __init__(self, repository: CartaRepository) -> None:
        self.repository = repository

    def listar_cartas(
        self,
        db: Session,
        *,
        ativo: bool | None = None,
        raridade: Raridade | None = None,
        tipo: Tipo | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Carta]:
        return self.repository.listar(
            db, ativo=ativo, raridade=raridade, tipo=tipo, skip=skip, limit=limit
        )

    def criar_carta(self, db: Session, dados: CartaCreate) -> Carta:
        return self.repository.criar(db, dados)

    def buscar_carta(self, db: Session, id: int) -> Carta:
        carta = self.repository.buscar_por_id(db, id)
        if not carta:
            raise HTTPException(status_code=404, detail=f"Carta com id {id} não encontrada")
        return carta

    def atualizar_carta(self, db: Session, id: int, dados: CartaUpdate) -> Carta:
        carta = self.buscar_carta(db, id)
        return self.repository.atualizar(db, carta, dados)

    def deletar_carta(self, db: Session, id: int) -> None:
        carta = self.buscar_carta(db, id)
        self.repository.deletar(db, carta)


carta_service = CartaService(carta_repository)
