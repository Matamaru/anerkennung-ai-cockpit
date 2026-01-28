#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.country                       *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Country as CountryORM
from backend.datamodule.sa import session_scope


class Country(Model):
    def __init__(self, name: str = None, abbreviation: str = None, description: str = None, id: str = None):
        self.id = id or str(uuid4())
        self.name = name
        self.abbreviation = abbreviation
        self.description = description

    def __repr__(self):
        return f"<Country name={self.name} abbreviation={self.abbreviation}>"
    
    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_country = CountryORM(
                    id=self.id,
                    name=self.name,
                    code=self.abbreviation,
                    description=self.description,
                )
                session.add(orm_country)
                session.flush()
                return Country._as_tuple(orm_country)
        except Exception as error:
            raise InsertError(error)
        
    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_country = session.query(CountryORM).filter_by(id=values[3]).first()
                if not orm_country:
                    raise UpdateError("Country not found.")
                orm_country.name = values[0]
                orm_country.code = values[1]
                orm_country.description = values[2]
                session.flush()
                return Country._as_tuple(orm_country)
        except Exception as error:
            raise UpdateError(error)

    def delete(self) -> tuple:
        try:
            with session_scope() as session:
                orm_country = session.query(CountryORM).filter_by(id=self.id).first()
                if not orm_country:
                    raise DeleteError("Country not found.")
                session.delete(orm_country)
                return Country._as_tuple(orm_country)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def from_tuple(tuple_country: tuple):
        if tuple_country:
            return Country(
                id=tuple_country[0],
                name=tuple_country[1],
                abbreviation=tuple_country[2],
                description=tuple_country[3]
            )
        return None
    
    @staticmethod
    def from_json(json_country: dict):
        if json_country:
            return Country(
                id=json_country.get("id"),
                name=json_country.get("name"),
                abbreviation=json_country.get("abbreviation"),
                description=json_country.get("description")
            )
        return None
    
    @staticmethod
    def get_by_id(id: str) -> tuple:
        with session_scope() as session:
            orm_country = session.query(CountryORM).filter_by(id=id).first()
            if not orm_country:
                raise RecordNotFoundError("Country not found in database.")
            return Country._as_tuple(orm_country)

    @staticmethod
    def get_by_name(name: str) -> tuple:
        with session_scope() as session:
            orm_country = session.query(CountryORM).filter_by(name=name).first()
            if not orm_country:
                raise RecordNotFoundError("Country not found in database.")
            return Country._as_tuple(orm_country)

    @staticmethod
    def get_all() -> tuple:
        with session_scope() as session:
            countries = session.query(CountryORM).all()
            return [Country._as_tuple(c) for c in countries]

    @staticmethod
    def get_by_code(code: str) -> tuple:
        with session_scope() as session:
            orm_country = session.query(CountryORM).filter_by(code=code).first()
            if not orm_country:
                raise RecordNotFoundError("Country not found in database.")
            return Country._as_tuple(orm_country)

    @staticmethod
    def create_default_countries() -> tuple:
        default_countries = [
            ("Germany", "DE", "Germany")
        ]
        try:
            with session_scope() as session:
                for country in default_countries:
                    existing = session.query(CountryORM).filter_by(code=country[1]).first()
                    if not existing:
                        orm_country = CountryORM(
                            id=str(uuid4()),
                            name=country[0],
                            code=country[1],
                            description=country[2],
                        )
                        session.add(orm_country)
                        print(f"Inserted default country '{country[0]}'.")
                    else:
                        print(f"Country '{country[0]}' already exists.")
            return Country.get_all()
        except Exception as error:
            raise InsertError(error)

    @staticmethod
    def _as_tuple(orm_country: CountryORM) -> tuple:
        return (orm_country.id, orm_country.name, orm_country.code, orm_country.description)
