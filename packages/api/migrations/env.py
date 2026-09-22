from alembic import context
from frontdesk_core.db import engine
from frontdesk_core import models  # noqa: F401
from sqlmodel import SQLModel

with engine().connect() as connection:
    context.configure(connection=connection, target_metadata=SQLModel.metadata)
    with context.begin_transaction():
        context.run_migrations()

