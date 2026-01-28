#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.application                   *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Application as ApplicationORM
from backend.datamodule.sa import session_scope


class Application(Model):
    def __init__(
            self,
            user_id: str = None,
            profession_id: str = None,
            country_id: str = None,
            state_id: str = None,
            time_created = None,
            id: str = None):
        self.id = id or str(uuid4())
        self.user_id = user_id
        self.profession_id = profession_id
        self.country_id = country_id
        self.state_id = state_id
        self.time_created = time_created

    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_app = ApplicationORM(
                    id=self.id,
                    user_id=self.user_id,
                    profession_id=self.profession_id,
                    country_id=self.country_id,
                    state_id=self.state_id,
                )
                session.add(orm_app)
                session.flush()
                return Application._as_tuple(orm_app)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_app = session.query(ApplicationORM).filter_by(id=values[4]).first()
                if not orm_app:
                    raise UpdateError("Application not found.")
                orm_app.user_id = values[0]
                orm_app.profession_id = values[1]
                orm_app.country_id = values[2]
                orm_app.state_id = values[3]
                session.flush()
                return Application._as_tuple(orm_app)
        except Exception as error:
            raise UpdateError(error)

    def delete(self) -> int:
        try:
            with session_scope() as session:
                deleted = session.query(ApplicationORM).filter_by(id=self.id).delete()
                return deleted
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            apps = session.query(ApplicationORM).all()
            return [Application._as_tuple(a) for a in apps]

    @staticmethod
    def get_by_id(application_id: str) -> tuple:
        with session_scope() as session:
            orm_app = session.query(ApplicationORM).filter_by(id=application_id).first()
            return Application._as_tuple(orm_app) if orm_app else None

    @staticmethod
    def get_by_profession_id(profession_id: str) -> list:
        with session_scope() as session:
            apps = session.query(ApplicationORM).filter_by(profession_id=profession_id).all()
            return [Application._as_tuple(a) for a in apps]

    @staticmethod
    def get_by_country_id(country_id: str) -> list:
        with session_scope() as session:
            apps = session.query(ApplicationORM).filter_by(country_id=country_id).all()
            return [Application._as_tuple(a) for a in apps]

    @staticmethod
    def get_by_state_id(state_id: str) -> list:
        with session_scope() as session:
            apps = session.query(ApplicationORM).filter_by(state_id=state_id).all()
            return [Application._as_tuple(a) for a in apps]

    @staticmethod
    def get_by_user_id(user_id: str) -> list:
        with session_scope() as session:
            apps = session.query(ApplicationORM).filter_by(user_id=user_id).all()
            return [Application._as_tuple(a) for a in apps]

    @staticmethod
    def from_tuple(t: tuple):
        return Application(
            id=t[0],
            user_id=t[1],
            profession_id=t[2],
            country_id=t[3],
            state_id=t[4],
            time_created=t[5],
        )

    @staticmethod
    def _as_tuple(orm_app: ApplicationORM) -> tuple:
        return (
            orm_app.id,
            orm_app.user_id,
            orm_app.profession_id,
            orm_app.country_id,
            orm_app.state_id,
            orm_app.time_created,
        )
