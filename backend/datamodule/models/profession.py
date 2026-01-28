#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.profession                    *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Profession as ProfessionORM
from backend.datamodule.sa import session_scope


class Profession(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_prof = ProfessionORM(id=self.id, name=self.name, description=self.description)
                session.add(orm_prof)
                session.flush()
                return Profession._as_tuple(orm_prof)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_prof = session.query(ProfessionORM).filter_by(id=values[2]).first()
                if not orm_prof:
                    raise UpdateError("Profession not found.")
                orm_prof.name = values[0]
                orm_prof.description = values[1]
                session.flush()
                return Profession._as_tuple(orm_prof)
        except Exception as error:
            raise UpdateError(error)

    def delete(self) -> int:
        try:
            with session_scope() as session:
                deleted = session.query(ProfessionORM).filter_by(id=self.id).delete()
                return deleted
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(profession_id: str) -> tuple:
        with session_scope() as session:
            orm_prof = session.query(ProfessionORM).filter_by(id=profession_id).first()
            return Profession._as_tuple(orm_prof) if orm_prof else None

    @staticmethod
    def get_by_name(name: str) -> tuple:
        with session_scope() as session:
            orm_prof = session.query(ProfessionORM).filter_by(name=name).first()
            return Profession._as_tuple(orm_prof) if orm_prof else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            profs = session.query(ProfessionORM).all()
            return [Profession._as_tuple(p) for p in profs]

    @staticmethod
    def from_tuple(t: tuple):
        return Profession(
            id=t[0],
            name=t[1],
            description=t[2]
        )

    @staticmethod
    def create_default_professions() -> list:
        default_professions = [
            ("Nurse", "Registered Nurse"),
        ]

        try:
            with session_scope() as session:
                for prof in default_professions:
                    existing = session.query(ProfessionORM).filter_by(name=prof[0]).first()
                    if not existing:
                        orm_prof = ProfessionORM(
                            id=str(uuid4()),
                            name=prof[0],
                            description=prof[1],
                        )
                        session.add(orm_prof)
            return Profession.get_all()
        except Exception as error:
            raise InsertError(error)

    @staticmethod
    def _as_tuple(orm_prof: ProfessionORM) -> tuple:
        return (orm_prof.id, orm_prof.name, orm_prof.description)
