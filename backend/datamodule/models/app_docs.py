#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.app_docs                      *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import AppDoc as AppDocORM, Document as DocumentORM, DocumentData as DocumentDataORM, DocumentType as DocumentTypeORM, File as FileORM, FileType as FileTypeORM, Status as StatusORM, User as UserORM
from backend.datamodule.sa import session_scope


class AppDocs(Model):
    def __init__(
            self, 
            application_id: str = None, 
            document_id: str = None, 
            requirements_id: str = None, 
            id: str = None):
        self.id = id or str(uuid4())
        self.application_id = application_id
        self.document_id = document_id
        self.requirements_id = requirements_id

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_app_docs = AppDocORM(
                    id=self.id,
                    application_id=self.application_id,
                    document_id=self.document_id,
                    requirements_id=self.requirements_id,
                )
                session.add(orm_app_docs)
                session.flush()
                return AppDocs._as_tuple(orm_app_docs)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_app_docs = session.query(AppDocORM).filter_by(id=values[3]).first()
                if not orm_app_docs:
                    raise UpdateError("AppDocs not found.")
                orm_app_docs.application_id = values[0]
                orm_app_docs.document_id = values[1]
                orm_app_docs.requirements_id = values[2]
                session.flush()
                return AppDocs._as_tuple(orm_app_docs)
        except Exception as error:
            raise UpdateError(error)

    def delete(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_app_docs = session.query(AppDocORM).filter_by(id=values[0]).first()
                if not orm_app_docs:
                    raise DeleteError("AppDocs not found.")
                session.delete(orm_app_docs)
                return AppDocs._as_tuple(orm_app_docs)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(app_docs_id: str) -> tuple:
        with session_scope() as session:
            orm_app_docs = session.query(AppDocORM).filter_by(id=app_docs_id).first()
            return AppDocs._as_tuple(orm_app_docs) if orm_app_docs else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            rows = session.query(AppDocORM).all()
            return [AppDocs._as_tuple(r) for r in rows]

    @staticmethod
    def get_by_application_id(application_id: str) -> list:
        with session_scope() as session:
            rows = session.query(AppDocORM).filter_by(application_id=application_id).all()
            return [AppDocs._as_tuple(r) for r in rows]

    @staticmethod
    def get_by_document_id(document_id: str) -> list:
        with session_scope() as session:
            rows = session.query(AppDocORM).filter_by(document_id=document_id).all()
            return [AppDocs._as_tuple(r) for r in rows]

    @staticmethod
    def get_by_requirements_id(requirements_id: str) -> list:
        with session_scope() as session:
            rows = session.query(AppDocORM).filter_by(requirements_id=requirements_id).all()
            return [AppDocs._as_tuple(r) for r in rows]

    @staticmethod
    def get_docs_for_application(application_id: str) -> list:
        with session_scope() as session:
            rows = (
                session.query(
                    DocumentORM.id.label("document_id"),
                    FileORM.id.label("file_id"),
                    DocumentORM.document_type_id,
                    FileTypeORM.id.label("file_type_id"),
                    DocumentDataORM.id.label("document_data_id"),
                    DocumentTypeORM.name.label("document_type_name"),
                    DocumentORM.last_modified,
                    DocumentORM.status_id,
                    StatusORM.name.label("status_name"),
                    FileORM.filename,
                    FileORM.filepath,
                    FileORM.filetype_id,
                    UserORM.user_id.label("user_id"),
                    DocumentDataORM.ocr_full_text,
                )
                .join(DocumentORM, AppDocORM.document_id == DocumentORM.id)
                .join(DocumentTypeORM, DocumentORM.document_type_id == DocumentTypeORM.id)
                .join(FileORM, DocumentORM.file_id == FileORM.id)
                .join(DocumentDataORM, DocumentORM.document_data_id == DocumentDataORM.id)
                .join(FileTypeORM, FileORM.filetype_id == FileTypeORM.id)
                .join(StatusORM, DocumentORM.status_id == StatusORM.id)
                .join(UserORM, DocumentORM.user_id == UserORM.user_id)
                .filter(AppDocORM.application_id == application_id)
                .all()
            )
            return [tuple(row) for row in rows]

    @staticmethod
    def from_tuple(t: tuple):
        return AppDocs(
            id=t[0],
            application_id=t[1],
            document_id=t[2],
            requirements_id=t[3],
        )

    @staticmethod
    def _as_tuple(orm_app_docs: AppDocORM) -> tuple:
        return (orm_app_docs.id, orm_app_docs.application_id, orm_app_docs.document_id, orm_app_docs.requirements_id)
