"""create cartas table

Revision ID: 0001
Revises:
Create Date: 2026-06-18 00:01:00

Esta é a migration inicial. Cria a tabela `cartas` com todos os campos
do modelo, incluindo os enums de raridade e tipo como colunas String
(o PostgreSQL valida via check constraint nas versões com Enum nativo,
mas String mantém a flexibilidade de adicionar novos valores sem migration).
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "cartas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(), nullable=False),
        sa.Column("preco", sa.Float(), nullable=False),
        sa.Column("estoque", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("raridade", sa.String(), nullable=False, server_default="Comum"),
        sa.Column("tipo", sa.String(), nullable=True),
        sa.Column("expansao", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_cartas_id"), "cartas", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_cartas_id"), table_name="cartas")
    op.drop_table("cartas")
