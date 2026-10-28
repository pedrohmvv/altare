"""guest invites

Revision ID: 0009
Revises: 0008
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: str | None = "0008"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

CHANNELS = "'WhatsApp', 'E-mail', 'Impresso', 'Pessoalmente', 'Outro'"
CHANNEL_CHECK = "ck_guest_households_guest_invite_channel"
TOGETHER_CHECK = "ck_guest_households_invite_date_and_channel_together"


def upgrade() -> None:
    # Em lote, porque o SQLite não acrescenta restrição a uma tabela que já existe.
    with op.batch_alter_table("guest_households") as batch:
        batch.add_column(
            sa.Column(
                "invite_sent_on",
                sa.Date(),
                comment="Quando o convite do núcleo foi enviado (F-CNV-05).",
            )
        )
        batch.add_column(
            sa.Column(
                "invite_channel",
                sa.String(12),
                comment="Canal do envio; anda junto com a data.",
            )
        )
        batch.create_check_constraint(op.f(CHANNEL_CHECK), f"invite_channel IN ({CHANNELS})")
        batch.create_check_constraint(
            op.f(TOGETHER_CHECK), "(invite_sent_on IS NULL) = (invite_channel IS NULL)"
        )


def downgrade() -> None:
    with op.batch_alter_table("guest_households") as batch:
        batch.drop_constraint(op.f(TOGETHER_CHECK), type_="check")
        batch.drop_constraint(op.f(CHANNEL_CHECK), type_="check")
        batch.drop_column("invite_channel")
        batch.drop_column("invite_sent_on")
