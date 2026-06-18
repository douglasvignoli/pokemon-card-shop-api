from pydantic import BaseModel, field_validator

from models import Raridade, Tipo


class CartaCreate(BaseModel):
    nome: str
    preco: float
    estoque: int = 0
    ativo: bool = True
    raridade: Raridade = Raridade.comum
    tipo: Tipo | None = None
    expansao: str | None = None

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
    """Todos os campos opcionais — PATCH atualiza apenas o que for enviado."""

    nome: str | None = None
    preco: float | None = None
    estoque: int | None = None
    ativo: bool | None = None
    raridade: Raridade | None = None
    tipo: Tipo | None = None
    expansao: str | None = None

    @field_validator("nome")
    @classmethod
    def nome_nao_pode_ser_vazio(cls, v: str | None) -> str | None:
        if v is not None and not v.strip():
            raise ValueError("nome não pode ser vazio ou conter apenas espaços")
        return v.strip() if v else v

    @field_validator("preco")
    @classmethod
    def preco_deve_ser_positivo(cls, v: float | None) -> float | None:
        if v is not None and v <= 0:
            raise ValueError("preco deve ser maior que zero")
        return v

    @field_validator("estoque")
    @classmethod
    def estoque_nao_pode_ser_negativo(cls, v: int | None) -> int | None:
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
    tipo: Tipo | None
    expansao: str | None

    model_config = {"from_attributes": True}
