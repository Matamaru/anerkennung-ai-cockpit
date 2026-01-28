#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.status                        *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Status as StatusORM
from backend.datamodule.sa import session_scope


class Status(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_status = StatusORM(id=self.id, name=self.name, description=self.description)
                session.add(orm_status)
                session.flush()
                return Status._as_tuple(orm_status)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_status = session.query(StatusORM).filter_by(id=values[2]).first()
                if not orm_status:
                    raise UpdateError("Status not found.")
                orm_status.name = values[0]
                orm_status.description = values[1]
                session.flush()
                return Status._as_tuple(orm_status)
        except Exception as error:
            raise UpdateError(error)

    def delete(self) -> int:
        try:
            with session_scope() as session:
                deleted = session.query(StatusORM).filter_by(id=self.id).delete()
                return deleted
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(status_id: str) -> tuple:
        with session_scope() as session:
            orm_status = session.query(StatusORM).filter_by(id=status_id).first()
            return Status._as_tuple(orm_status) if orm_status else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            statuses = session.query(StatusORM).all()
            return [Status._as_tuple(s) for s in statuses]

    @staticmethod
    def get_by_name(name: str) -> tuple:
        with session_scope() as session:
            orm_status = session.query(StatusORM).filter_by(name=name).first()
            return Status._as_tuple(orm_status) if orm_status else None

    @staticmethod
    def create_default_statuses():
        default_statuses = [
            {"name": "new", "description": "Newly created"},
            {"name": "in_progress", "description": "In progress"},
            {"name": "completed", "description": "Completed"},
        ]
        try:
            with session_scope() as session:
                for status in default_statuses:
                    existing = session.query(StatusORM).filter_by(name=status["name"]).first()
                    if not existing:
                        session.add(StatusORM(
                            id=str(uuid4()),
                            name=status["name"],
                            description=status["description"],
                        ))
        except Exception as error:
            raise InsertError(error)

    @staticmethod
    def from_tuple(t: tuple):
        return Status(
            id=t[0],
            name=t[1],
            description=t[2]
        )

    @staticmethod
    def _as_tuple(orm_status: StatusORM) -> tuple:
        return (orm_status.id, orm_status.name, orm_status.description)
