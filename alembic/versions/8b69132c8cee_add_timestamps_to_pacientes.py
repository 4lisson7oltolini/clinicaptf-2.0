"""add timestamps to pacientes"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8b69132c8cee"
down_revision = "93bf205e4433"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Adiciona atualizado_em temporariamente permitindo NULL
    op.add_column(
        "pacientes",
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            nullable=True
        )
    )

    # 2. Preenche os registros existentes
    # Usa criado_em como valor inicial de atualizado_em
    op.execute(
        sa.text(
            """
            UPDATE pacientes
            SET atualizado_em = criado_em
            WHERE atualizado_em IS NULL
            """
        )
    )

    # 3. Garante que criado_em não possua NULL
    op.execute(
        sa.text(
            """
            UPDATE pacientes
            SET criado_em = CURRENT_TIMESTAMP
            WHERE criado_em IS NULL
            """
        )
    )

    # 4. SQLite precisa recriar a tabela para alterar nullable
    with op.batch_alter_table("pacientes") as batch_op:
        batch_op.alter_column(
            "atualizado_em",
            existing_type=sa.DateTime(timezone=True),
            nullable=False
        )

        batch_op.alter_column(
            "criado_em",
            existing_type=sa.DateTime(timezone=True),
            nullable=False
        )


def downgrade() -> None:
    with op.batch_alter_table("pacientes") as batch_op:
        batch_op.alter_column(
            "criado_em",
            existing_type=sa.DateTime(timezone=True),
            nullable=True
        )

        batch_op.drop_column("atualizado_em")