"""Initial logistics schema."""
from alembic import op
from frontdesk_core import models  # noqa: F401
from sqlmodel import SQLModel

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None

def upgrade() -> None:
    SQLModel.metadata.create_all(op.get_bind())

def downgrade() -> None:
    SQLModel.metadata.drop_all(op.get_bind())

