from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Configure engine for SQLite or Postgres
connect_args = {}
if str(settings.DATABASE_URL).startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine = create_engine(
    str(settings.DATABASE_URL),
    pool_pre_ping=True,
    connect_args=connect_args
)

# Enable WAL mode for SQLite to improve concurrency
if str(settings.DATABASE_URL).startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

# Configured generic un-bound Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
