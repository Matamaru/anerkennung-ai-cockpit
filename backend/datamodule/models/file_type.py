#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.file_type                     *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import FileType as FileTypeORM
from backend.datamodule.sa import session_scope


class FileType(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_ft = FileTypeORM(id=self.id, name=self.name, description=self.description)
                session.add(orm_ft)
                session.flush()
                return FileType._as_tuple(orm_ft)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_ft = session.query(FileTypeORM).filter_by(id=values[2]).first()
                if not orm_ft:
                    raise UpdateError("File type not found.")
                orm_ft.name = values[0]
                orm_ft.description = values[1]
                session.flush()
                return FileType._as_tuple(orm_ft)
        except Exception as error:
            raise UpdateError(error)

    def delete(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_ft = session.query(FileTypeORM).filter_by(id=values[0]).first()
                if not orm_ft:
                    raise DeleteError("File type not found.")
                session.delete(orm_ft)
                return FileType._as_tuple(orm_ft)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(file_type_id: str) -> tuple:
        with session_scope() as session:
            orm_ft = session.query(FileTypeORM).filter_by(id=file_type_id).first()
            return FileType._as_tuple(orm_ft) if orm_ft else None

    @staticmethod
    def get_by_name(name: str) -> tuple:
        with session_scope() as session:
            orm_ft = session.query(FileTypeORM).filter_by(name=name).first()
            return FileType._as_tuple(orm_ft) if orm_ft else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            types = session.query(FileTypeORM).all()
            return [FileType._as_tuple(t) for t in types]

    @staticmethod
    def create_default_file_types():
        default_types = [
            {"name": "PDF",  "description": "PDF Document"},
            {"name": "JPEG", "description": "JPEG Image"},
            {"name": "PNG",  "description": "PNG Image"},
        ]
        try:
            with session_scope() as session:
                for ft in default_types:
                    existing = session.query(FileTypeORM).filter_by(name=ft["name"]).first()
                    if not existing:
                        session.add(FileTypeORM(
                            id=str(uuid4()),
                            name=ft["name"],
                            description=ft["description"],
                        ))
        except Exception as error:
            raise InsertError(error)

    @staticmethod
    def from_tuple(t: tuple):
        return FileType(id=t[0], name=t[1], description=t[2])

    @staticmethod
    def _as_tuple(orm_ft: FileTypeORM) -> tuple:
        return (orm_ft.id, orm_ft.name, orm_ft.description)
