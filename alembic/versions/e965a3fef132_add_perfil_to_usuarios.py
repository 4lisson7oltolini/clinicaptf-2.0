"""add perfil to usuarios

Revision ID: e965a3fef132
Revises: 8b69132c8cee
Create Date: 2026-09-16 09:24:45.022993

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e965a3fef132"
down_revision: Union[str, Sequence[str], None] = "8b69132c8cee"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona o perfil aos usuários existentes."""

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.add_column(
            sa.Column(
                "perfil",
                sa.String(length=30),
                nullable=True,
                server_default="profissional",
            )
        )

    op.execute(
        "UPDATE usuarios "
        "SET perfil = 'profissional' "
        "WHERE perfil IS NULL"
    )

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.alter_column(
            "perfil",
            existing_type=sa.String(length=30),
            nullable=False,
            server_default=None,
        )


def downgrade() -> None:
    """Remove o perfil dos usuários."""

    with op.batch_alter_table("usuarios") as batch_op:
        batch_op.drop_column("perfil")