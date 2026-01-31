from __future__ import annotations

from datetime import datetime
from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.datamodule.sa import Base


class Role(Base):
    __tablename__ = "_roles"

    role_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    role_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class User(Base):
    __tablename__ = "_users"

    user_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    role_id: Mapped[str] = mapped_column(String(255), ForeignKey("_roles.role_id"), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    b_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    salt: Mapped[str] = mapped_column(String(255), nullable=False)
    pepper: Mapped[str] = mapped_column(String(255), nullable=False)

    role = relationship("Role")


class FileType(Base):
    __tablename__ = "_file_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class File(Base):
    __tablename__ = "_files"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(Text, nullable=False)
    filetype_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_file_types.id"))
    uploaded_at: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())

    filetype = relationship("FileType")


class DocumentType(Base):
    __tablename__ = "_document_types"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class DocumentData(Base):
    __tablename__ = "_document_datas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    ocr_doc_type_prediction_str: Mapped[str | None] = mapped_column(Text)
    ocr_predictions_str: Mapped[str | None] = mapped_column(Text)
    ocr_full_text: Mapped[str | None] = mapped_column(Text)
    ocr_extracted_data: Mapped[dict | None] = mapped_column(JSON)
    layoutlm_full_text: Mapped[str | None] = mapped_column(Text)
    layout_lm_data: Mapped[dict | None] = mapped_column(JSON)


class Status(Base):
    __tablename__ = "_statuses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class Document(Base):
    __tablename__ = "_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    file_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_files.id"))
    document_type_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_document_types.id"))
    document_data_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_document_datas.id"))
    user_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_users.user_id"))
    status_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_statuses.id"))
    last_modified: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())

    file = relationship("File")
    document_type = relationship("DocumentType")
    document_data = relationship("DocumentData")
    user = relationship("User")
    status = relationship("Status")


class Country(Base):
    __tablename__ = "_countries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class State(Base):
    __tablename__ = "_states"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    country_id: Mapped[str] = mapped_column(String(36), ForeignKey("_countries.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    abbreviation: Mapped[str] = mapped_column(String(10), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)

    country = relationship("Country")


class Profession(Base):
    __tablename__ = "_professions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)


class Requirement(Base):
    __tablename__ = "_requirements"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    profession_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_professions.id"))
    country_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_countries.id"))
    state_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_states.id"))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    optional: Mapped[bool] = mapped_column(Boolean, default=False)
    translation_required: Mapped[bool] = mapped_column(Boolean, default=False)
    fullfilled: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_multiple: Mapped[bool] = mapped_column(Boolean, default=True)

    profession = relationship("Profession")
    country = relationship("Country")
    state = relationship("State")


class Application(Base):
    __tablename__ = "_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("_users.user_id"), nullable=False)
    profession_id: Mapped[str] = mapped_column(String(36), ForeignKey("_professions.id"), nullable=False)
    country_id: Mapped[str] = mapped_column(String(36), ForeignKey("_countries.id"), nullable=False)
    state_id: Mapped[str] = mapped_column(String(36), ForeignKey("_states.id"), nullable=False)
    time_created: Mapped[datetime | None] = mapped_column(DateTime, server_default=func.now())

    user = relationship("User")
    profession = relationship("Profession")
    country = relationship("Country")
    state = relationship("State")


class AppDoc(Base):
    __tablename__ = "_app_docs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    application_id: Mapped[str] = mapped_column(String(36), ForeignKey("_applications.id"), nullable=False)
    document_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("_documents.id"))
    requirements_id: Mapped[str] = mapped_column(String(36), ForeignKey("_requirements.id"), nullable=False)

    application = relationship("Application")
    document = relationship("Document")
    requirement = relationship("Requirement")
