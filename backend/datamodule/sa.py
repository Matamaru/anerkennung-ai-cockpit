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


def _ensure_document_review_columns() -> None:
    try:
        with engine.begin() as conn:
            if conn.dialect.name == "sqlite":
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(_document_datas)")).fetchall()]
                if "review_status" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN review_status TEXT"))
                if "review_comment" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN review_comment TEXT"))
                if "reviewed_by" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN reviewed_by VARCHAR(36)"))
                if "reviewed_at" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN reviewed_at TIMESTAMP"))
            else:
                cols = {
                    row[0]
                    for row in conn.execute(
                        text(
                            "SELECT column_name FROM information_schema.columns "
                            "WHERE table_name = '_document_datas'"
                        )
                    ).fetchall()
                }
                if "review_status" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN review_status TEXT"))
                if "review_comment" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN review_comment TEXT"))
                if "reviewed_by" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN reviewed_by VARCHAR(36)"))
                if "reviewed_at" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN reviewed_at TIMESTAMP"))
    except Exception:
        pass


_ensure_document_review_columns()

def _ensure_document_ocr_source_column() -> None:
    try:
        with engine.begin() as conn:
            if conn.dialect.name == "sqlite":
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(_document_datas)")).fetchall()]
                if "ocr_source" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN ocr_source TEXT"))
            else:
                cols = {
                    row[0]
                    for row in conn.execute(
                        text(
                            "SELECT column_name FROM information_schema.columns "
                            "WHERE table_name = '_document_datas'"
                        )
                    ).fetchall()
                }
                if "ocr_source" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN ocr_source TEXT"))
    except Exception:
        pass


_ensure_document_ocr_source_column()

def _ensure_document_check_ready_columns() -> None:
    try:
        with engine.begin() as conn:
            if conn.dialect.name == "sqlite":
                cols = [row[1] for row in conn.execute(text("PRAGMA table_info(_document_datas)")).fetchall()]
                if "check_ready" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN check_ready BOOLEAN DEFAULT 0"))
                if "validation_errors" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN validation_errors JSON"))
            else:
                cols = {
                    row[0]
                    for row in conn.execute(
                        text(
                            "SELECT column_name FROM information_schema.columns "
                            "WHERE table_name = '_document_datas'"
                        )
                    ).fetchall()
                }
                if "check_ready" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN check_ready BOOLEAN DEFAULT FALSE"))
                if "validation_errors" not in cols:
                    conn.execute(text("ALTER TABLE _document_datas ADD COLUMN validation_errors JSONB"))
    except Exception:
        pass


_ensure_document_check_ready_columns()


def _ensure_user_profile_table() -> None:
    try:
        with engine.begin() as conn:
            if conn.dialect.name == "sqlite":
                conn.execute(
                    text(
                        "CREATE TABLE IF NOT EXISTS _user_profiles ("
                        "user_id VARCHAR(255) PRIMARY KEY, "
                        "first_name VARCHAR(255), "
                        "last_name VARCHAR(255), "
                        "birth_date VARCHAR(50), "
                        "nationality VARCHAR(100), "
                        "address_line1 VARCHAR(255), "
                        "address_line2 VARCHAR(255), "
                        "postal_code VARCHAR(50), "
                        "city VARCHAR(100), "
                        "country VARCHAR(100), "
                        "phone VARCHAR(50), "
                        "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                        ")"
                    )
                )
            else:
                exists = conn.execute(
                    text(
                        "SELECT 1 FROM information_schema.tables "
                        "WHERE table_name = '_user_profiles'"
                    )
                ).fetchone()
                if not exists:
                    conn.execute(
                        text(
                            "CREATE TABLE _user_profiles ("
                            "user_id VARCHAR(255) PRIMARY KEY REFERENCES _users(user_id) ON DELETE CASCADE, "
                            "first_name VARCHAR(255), "
                            "last_name VARCHAR(255), "
                            "birth_date VARCHAR(50), "
                            "nationality VARCHAR(100), "
                            "address_line1 VARCHAR(255), "
                            "address_line2 VARCHAR(255), "
                            "postal_code VARCHAR(50), "
                            "city VARCHAR(100), "
                            "country VARCHAR(100), "
                            "phone VARCHAR(50), "
                            "updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                            ")"
                        )
                    )
    except Exception:
        pass


_ensure_user_profile_table()


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
