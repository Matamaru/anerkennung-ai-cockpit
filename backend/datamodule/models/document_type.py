#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_type                 *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import DocumentType as DocumentTypeORM
from backend.datamodule.sa import session_scope


class DocumentType(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_dt = DocumentTypeORM(id=self.id, name=self.name, description=self.description)
                session.add(orm_dt)
                session.flush()
                return DocumentType._as_tuple(orm_dt)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_dt = session.query(DocumentTypeORM).filter_by(id=values[2]).first()
                if not orm_dt:
                    raise UpdateError("Document type not found.")
                orm_dt.name = values[0]
                orm_dt.description = values[1]
                session.flush()
                return DocumentType._as_tuple(orm_dt)
        except Exception as error:
            raise UpdateError(error)

    def delete(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_dt = session.query(DocumentTypeORM).filter_by(id=values[0]).first()
                if not orm_dt:
                    raise DeleteError("Document type not found.")
                session.delete(orm_dt)
                return DocumentType._as_tuple(orm_dt)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(id: str) -> tuple:
        with session_scope() as session:
            orm_dt = session.query(DocumentTypeORM).filter_by(id=id).first()
            return DocumentType._as_tuple(orm_dt) if orm_dt else None

    @staticmethod
    def get_by_name(name: str) -> tuple:
        with session_scope() as session:
            orm_dt = session.query(DocumentTypeORM).filter_by(name=name).first()
            return DocumentType._as_tuple(orm_dt) if orm_dt else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            types = session.query(DocumentTypeORM).all()
            return [DocumentType._as_tuple(t) for t in types]

    @staticmethod
    def from_tuple(t: tuple):
        return DocumentType(id=t[0], name=t[1], description=t[2])

    @staticmethod
    def create_default_document_types():
        default_types = [
            ("passport", "Passport"),
            ("diploma", "Degree Certificate"),
        ]
        try:
            with session_scope() as session:
                for dt in default_types:
                    existing = session.query(DocumentTypeORM).filter_by(name=dt[0]).first()
                    if not existing:
                        session.add(DocumentTypeORM(
                            id=str(uuid4()),
                            name=dt[0],
                            description=dt[1],
                        ))
        except Exception as error:
            raise InsertError(error)

    @staticmethod
    def _as_tuple(orm_dt: DocumentTypeORM) -> tuple:
        return (orm_dt.id, orm_dt.name, orm_dt.description)
