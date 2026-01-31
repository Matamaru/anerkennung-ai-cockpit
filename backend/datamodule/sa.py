from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()


def _database_url() -> str:
    sqlite_path = os.getenv("SQLITE_PATH")
    if sqlite_path:
        return f"sqlite:///{sqlite_path}"

    url = os.getenv("DATABASE_URL")
    if url:
        if url.startswith("postgres://"):
            return url.replace("postgres://", "postgresql://", 1)
        return url

    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if not all([name, user, password]):
        missing = [k for k, v in {"DB_NAME": name, "DB_USER": user, "DB_PASSWORD": password}.items() if not v]
        raise ValueError(f"Missing DB config values: {', '.join(missing)}")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{name}"


DATABASE_URL = _database_url()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def _ensure_requirements_allow_multiple_column() -> None:
    try:
        with engine.begin() as conn:
            if conn.dialect.name == "sqlite":
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(_requirements)")).fetchall()]
                if "allow_multiple" not in cols:
                    conn.execute(text("ALTER TABLE _requirements ADD COLUMN allow_multiple BOOLEAN DEFAULT 1"))
            else:
                exists = conn.execute(
                    text(
                        "SELECT 1 FROM information_schema.columns "
                        "WHERE table_name = '_requirements' AND column_name = 'allow_multiple'"
                    )
                ).fetchone()
                if not exists:
                    conn.execute(text("ALTER TABLE _requirements ADD COLUMN allow_multiple BOOLEAN DEFAULT TRUE"))
                    conn.execute(
                        text(
                            "UPDATE _requirements SET allow_multiple = FALSE "
                            "WHERE lower(name) IN ('id','cv','proofofberlinresponsibility','passport')"
                        )
                    )
    except Exception:
        # Best-effort migration; ignore if DB user lacks permissions.
        pass


_ensure_requirements_allow_multiple_column()


@contextmanager
def session_scope() -> Iterator:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
