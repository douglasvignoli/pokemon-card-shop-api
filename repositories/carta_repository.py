from sqlalchemy.orm import Session

from models import Carta, Raridade, Tipo
from schemas import CartaCreate, CartaUpdate


class CartaRepository:
    """Responsável exclusivamente pelo acesso ao banco de dados.

    Nenhuma regra de negócio aqui — só queries SQLAlchemy.
    Isso permite trocar o ORM ou o banco sem tocar no restante da aplicação.
    """

    def listar(
        self,
        db: Session,
        *,
        ativo: bool | None = None,
        raridade: Raridade | None = None,
        tipo: Tipo | None = None,
        skip: int = 0,
        limit: int = 100,
    ) -> list[Carta]:
        query = db.query(Carta)
        if ativo is not None:
            query = query.filter(Carta.ativo == ativo)
        if raridade is not None:
            query = query.filter(Carta.raridade == raridade.value)
        if tipo is not None:
            query = query.filter(Carta.tipo == tipo.value)
        return query.offset(skip).limit(limit).all()

    def buscar_por_id(self, db: Session, id: int) -> Carta | None:
        return db.query(Carta).filter(Carta.id == id).first()

    def criar(self, db: Session, dados: CartaCreate) -> Carta:
        carta = Carta(**dados.model_dump())
        db.add(carta)
        db.commit()
        db.refresh(carta)
        return carta

    def atualizar(self, db: Session, carta: Carta, dados: CartaUpdate) -> Carta:
        for campo, valor in dados.model_dump(exclude_unset=True).items():
            setattr(carta, campo, valor)
        db.commit()
        db.refresh(carta)
        return carta

    def deletar(self, db: Session, carta: Carta) -> None:
        db.delete(carta)
        db.commit()


carta_repository = CartaRepository()
