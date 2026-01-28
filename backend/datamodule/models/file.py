#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.file                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import File as FileORM, FileType as FileTypeORM
from backend.datamodule.sa import session_scope


class File(Model):
    def __init__(self, filename: str = None, filepath: str = None, filetype_id: str = None, id: str = None):
        self.id = id or str(uuid4())
        self.filename = filename
        self.filepath = filepath
        self.filetype_id = filetype_id

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_file = FileORM(
                    id=self.id,
                    filename=self.filename,
                    filepath=self.filepath,
                    filetype_id=self.filetype_id,
                )
                session.add(orm_file)
                session.flush()
                return File._as_tuple(orm_file)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_file = session.query(FileORM).filter_by(id=values[3]).first()
                if not orm_file:
                    raise UpdateError("File not found.")
                orm_file.filename = values[0]
                orm_file.filepath = values[1]
                orm_file.filetype_id = values[2]
                session.flush()
                return File._as_tuple(orm_file)
        except Exception as error:
            raise UpdateError(error)

    def delete(self, value: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_file = session.query(FileORM).filter_by(id=value[0]).first()
                if not orm_file:
                    raise DeleteError("File not found.")
                session.delete(orm_file)
                return File._as_tuple(orm_file)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(id: str) -> tuple:
        with session_scope() as session:
            orm_file = session.query(FileORM).filter_by(id=id).first()
            return File._as_tuple(orm_file) if orm_file else None

    @staticmethod
    def get_by_name(filename: str) -> tuple:
        with session_scope() as session:
            orm_file = session.query(FileORM).filter_by(filename=filename).first()
            return File._as_tuple(orm_file) if orm_file else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            files = session.query(FileORM).all()
            return [File._as_tuple(f) for f in files]

    @staticmethod
    def get_all_by_filetype_name(filetype_name: str) -> list:
        with session_scope() as session:
            files = (
                session.query(FileORM)
                .join(FileTypeORM, FileORM.filetype_id == FileTypeORM.id)
                .filter(FileTypeORM.name == filetype_name)
                .all()
            )
            return [File._as_tuple(f) for f in files]

    @staticmethod
    def from_tuple(t: tuple):
        return File(
            id=t[0],
            filename=t[1],
            filepath=t[2],
            filetype_id=t[3],
        )

    @staticmethod
    def _as_tuple(orm_file: FileORM) -> tuple:
        return (orm_file.id, orm_file.filename, orm_file.filepath, orm_file.filetype_id, orm_file.uploaded_at)
