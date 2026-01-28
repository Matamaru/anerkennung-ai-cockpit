#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document                      *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Document as DocumentORM
from backend.datamodule.sa import session_scope


class Document(Model):
    def __init__(
            self,
            file_id: str = None,
            document_type_id: str = None,
            document_data_id: str = None,
            user_id: str = None,
            status_id: str = None,
            last_modified = None,
            id: str = None):
        self.id = id or str(uuid4())
        self.file_id = file_id
        self.document_type_id = document_type_id
        self.document_data_id = document_data_id
        self.user_id = user_id
        self.status_id = status_id
        self.last_modified = last_modified

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_doc = DocumentORM(
                    id=self.id,
                    file_id=self.file_id,
                    document_type_id=self.document_type_id,
                    document_data_id=self.document_data_id,
                    user_id=self.user_id,
                    status_id=self.status_id,
                    last_modified=self.last_modified,
                )
                session.add(orm_doc)
                session.flush()
                return Document._as_tuple(orm_doc)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_doc = session.query(DocumentORM).filter_by(id=values[6]).first()
                if not orm_doc:
                    raise UpdateError("Document not found.")
                orm_doc.file_id = values[0]
                orm_doc.document_type_id = values[1]
                orm_doc.document_data_id = values[2]
                orm_doc.user_id = values[3]
                orm_doc.status_id = values[4]
                orm_doc.last_modified = values[5]
                session.flush()
                return Document._as_tuple(orm_doc)
        except Exception as error:
            raise UpdateError(error)

    def delete(self, value: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_doc = session.query(DocumentORM).filter_by(id=value[0]).first()
                if not orm_doc:
                    raise DeleteError("Document not found.")
                session.delete(orm_doc)
                return Document._as_tuple(orm_doc)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(document_id: str) -> tuple:
        with session_scope() as session:
            orm_doc = session.query(DocumentORM).filter_by(id=document_id).first()
            return Document._as_tuple(orm_doc) if orm_doc else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            docs = session.query(DocumentORM).all()
            return [Document._as_tuple(d) for d in docs]

    @staticmethod
    def get_by_user_id(user_id: str) -> list:
        with session_scope() as session:
            docs = session.query(DocumentORM).filter_by(user_id=user_id).all()
            return [Document._as_tuple(d) for d in docs]

    @staticmethod
    def get_by_status_id(status_id: str) -> list:
        with session_scope() as session:
            docs = session.query(DocumentORM).filter_by(status_id=status_id).all()
            return [Document._as_tuple(d) for d in docs]

    @staticmethod
    def get_by_document_type_id(document_type_id: str) -> list:
        with session_scope() as session:
            docs = session.query(DocumentORM).filter_by(document_type_id=document_type_id).all()
            return [Document._as_tuple(d) for d in docs]

    @staticmethod
    def get_by_file_id(file_id: str) -> list:
        with session_scope() as session:
            docs = session.query(DocumentORM).filter_by(file_id=file_id).all()
            return [Document._as_tuple(d) for d in docs]

    @staticmethod
    def get_by_status_and_user_id(status_id: str, user_id: str) -> list:
        with session_scope() as session:
            docs = session.query(DocumentORM).filter_by(status_id=status_id, user_id=user_id).all()
            return [Document._as_tuple(d) for d in docs]

    @staticmethod
    def from_tuple(t: tuple):
        return Document(
            id=t[0],
            file_id=t[1],
            document_type_id=t[2],
            document_data_id=t[3],
            user_id=t[4],
            status_id=t[5],
            last_modified=t[6],
        )

    @staticmethod
    def _as_tuple(orm_doc: DocumentORM) -> tuple:
        return (
            orm_doc.id,
            orm_doc.file_id,
            orm_doc.document_type_id,
            orm_doc.document_data_id,
            orm_doc.user_id,
            orm_doc.status_id,
            orm_doc.last_modified,
        )
