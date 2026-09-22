from sqlalchemy import Engine, create_engine
from frontdesk_core.config import Settings

def engine(url: str | None = None) -> Engine:
    return create_engine(url or Settings().database_url, pool_size=60, max_overflow=0, pool_pre_ping=True, hide_parameters=True)

