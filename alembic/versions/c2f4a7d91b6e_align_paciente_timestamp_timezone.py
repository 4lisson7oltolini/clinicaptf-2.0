"""align paciente timestamp timezone

Revision ID: c2f4a7d91b6e
Revises: 7b3f32d0e094
Create Date: 2026-09-22

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c2f4a7d91b6e"
down_revision: Union[str, Sequence[str], None] = "7b3f32d0e094"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Alinha criado_em ao DateTime com timezone do modelo Paciente."""

    with op.batch_alter_table("pacientes") as batch_op:
        batch_op.alter_column(
            "criado_em",
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Reverte criado_em para timestamp sem timezone."""

    with op.batch_alter_table("pacientes") as batch_op:
        batch_op.alter_column(
            "criado_em",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=False,
        )
