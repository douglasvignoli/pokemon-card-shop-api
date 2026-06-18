from enum import Enum

from sqlalchemy import Boolean, Column, Float, Integer, String

from database import Base


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
