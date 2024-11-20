from typing import Any, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker
import os

# ...existing code...

Base = declarative_base()


class DatabaseEngine:
    _engine = None

    @classmethod
    def get_postgres_engine(cls):
        if cls._engine is None:
            user = os.getenv('DB_USER')
            password = os.getenv('DB_PASSWORD')
            host = os.getenv('DB_HOST')
            port = os.getenv('DB_PORT')
            dbname = os.getenv('DB_NAME')

            if not all([user, password, host, port, dbname]):
                raise ValueError(
                    "Database connection parameters must be provided through environment variables.")
            url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
            cls._engine = create_engine(url)
        return cls._engine


def get_session() -> Generator[Session, Any, Any]:
    engine = DatabaseEngine.get_postgres_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
