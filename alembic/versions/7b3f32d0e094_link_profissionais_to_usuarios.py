"""link profissionais to usuarios

Revision ID: 7b3f32d0e094
Revises: e965a3fef132
Create Date: 2026-09-16 09:56:49.400688

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7b3f32d0e094"
down_revision: Union[str, Sequence[str], None] = "e965a3fef132"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Cria o vínculo entre profissionais e usuários."""

    with op.batch_alter_table("profissionais") as batch_op:

        batch_op.add_column(
            sa.Column(
                "usuario_id",
                sa.Integer(),
                nullable=True,
            )
        )

        batch_op.create_unique_constraint(
            "uq_profissionais_usuario_id",
            ["usuario_id"],
        )

        batch_op.create_foreign_key(
            "fk_profissionais_usuario_id",
            "usuarios",
            ["usuario_id"],
            ["id"],
        )


def downgrade() -> None:
    """Remove o vínculo entre profissionais e usuários."""

    with op.batch_alter_table("profissionais") as batch_op:

        batch_op.drop_constraint(
            "fk_profissionais_usuario_id",
            type_="foreignkey",
        )

        batch_op.drop_constraint(
            "uq_profissionais_usuario_id",
            type_="unique",
        )

        batch_op.drop_column("usuario_id")
