"""schedule windows

Revision ID: 0012
Revises: 0011
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _foreign_keys(enabled: bool) -> None:
    """O lote recria a tabela (copia, apaga e renomeia), e apagar `milestones` com as dependências
    e o histórico apontando para ela falha com as chaves estrangeiras ligadas. O `PRAGMA` só vale
    fora de uma transação, então vem antes de qualquer escrita; o PostgreSQL não o conhece."""
    if op.get_bind().dialect.name == "sqlite":
        op.execute(sa.text(f"PRAGMA foreign_keys={'ON' if enabled else 'OFF'}"))


def upgrade() -> None:
    # Sem lote: acrescentar uma coluna com valor padrão o SQLite faz no lugar. `sa.false()` e não
    # `text("0")`, porque o PostgreSQL não aceita `0` como padrão de uma coluna booleana. A
    # semente fica como está: nenhuma janela dela foi editada.
    op.add_column(
        "milestones",
        sa.Column(
            "window_edited",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
            comment=(
                "Verdadeiro se o casal editou a janela; falso é a sugestão genérica da semente "
                "(F-CRN-02). Sem janela, falso."
            ),
        ),
    )


def downgrade() -> None:
    # Em lote, porque o SQLite recria a tabela para tirar a coluna; as restrições nomeadas da
    # janela (da 0010) e as da 0011 vão junto na cópia.
    _foreign_keys(False)
    with op.batch_alter_table("milestones") as batch:
        batch.drop_column("window_edited")
    _foreign_keys(True)
