#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.state                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Country as CountryORM, State as StateORM
from backend.datamodule.sa import session_scope


class State(Model):
    def __init__(self, 
                 id: str = None, 
                 country_id: str = None, 
                 name: str = None, 
                 abbreviation: str = None, 
                 description: str = None):
        self.id = id or str(uuid4())
        self.country_id = country_id
        self.name = name
        self.abbreviation = abbreviation
        self.description = description

    def __repr__(self):
        return f"<State name={self.name} abbreviation={self.abbreviation}>"
    
    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                existing = session.query(StateORM).filter_by(name=self.name).first()
                if existing:
                    raise InsertError(f"State with name '{self.name}' already exists in database.")
                orm_state = StateORM(
                    id=self.id,
                    country_id=self.country_id,
                    name=self.name,
                    abbreviation=self.abbreviation,
                    description=self.description,
                )
                session.add(orm_state)
                session.flush()
                return State._as_tuple(orm_state)
        except Exception as error:
            raise InsertError(error)
            
    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_state = session.query(StateORM).filter_by(id=values[4]).first()
                if not orm_state:
                    raise UpdateError("Failed to update state in database.")
                orm_state.country_id = values[0]
                orm_state.name = values[1]
                orm_state.abbreviation = values[2]
                orm_state.description = values[3]
                session.flush()
                return State._as_tuple(orm_state)
        except Exception as error:
            raise UpdateError(error)

    def delete(self):
        try:
            with session_scope() as session:
                orm_state = session.query(StateORM).filter_by(id=self.id).first()
                if not orm_state:
                    raise DeleteError("State not found.")
                session.delete(orm_state)
                return self.id
        except Exception as error:
            raise DeleteError(error)
        
    @staticmethod
    def get_by_id(state_id: str) -> tuple:
        with session_scope() as session:
            orm_state = session.query(StateORM).filter_by(id=state_id).first()
            return State._as_tuple(orm_state) if orm_state else None

    @staticmethod
    def get_by_name(name: str) -> tuple:
        with session_scope() as session:
            orm_state = session.query(StateORM).filter_by(name=name).first()
            return State._as_tuple(orm_state) if orm_state else None

    @staticmethod
    def get_by_code(code: str) -> tuple:
        with session_scope() as session:
            orm_state = session.query(StateORM).filter_by(abbreviation=code).first()
            return State._as_tuple(orm_state) if orm_state else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            states = session.query(StateORM).all()
            return [State._as_tuple(s) for s in states]

    @staticmethod   
    def from_json(data: dict):
        return State(
            id=data.get("id"),
            country_id=data.get("country_id"),
            name=data.get("name"),
            abbreviation=data.get("abbreviation"),
            description=data.get("description")
        )
    
    @staticmethod
    def from_tuple(t: tuple):
        return State(
            id=t[0],
            country_id=t[1],
            name=t[2],
            abbreviation=t[3],
            description=t[4]
        )

    @staticmethod
    def state_in_db(name: str):
        with session_scope() as session:
            orm_state = session.query(StateORM).filter_by(name=name).first()
            if orm_state:
                return True, State._as_tuple(orm_state)
            return False, None
        
    @staticmethod
    def create_default_states():
        default_states = [
            {
               "name": "Bavaria",
               "abbreviation": "DE-BY",
               "description": "Bayern",
               "country_code": "DE"
           },
           {
               "name": "Berlin",
               "abbreviation": "DE-BE",
               "description": "Berlin",
               "country_code": "DE"
           },
           {
               "name": "North Rhine-Westphalia",
               "abbreviation": "DE-NW",
               "description": "Nordrhein-Westfalen",
               "country_code": "DE"
           }
        ]

        try:
            with session_scope() as session:
                for state in default_states:
                    existing = session.query(StateORM).filter_by(name=state["name"]).first()
                    country = session.query(CountryORM).filter_by(code=state["country_code"]).first()
                    if not country:
                        print(f"Country with code '{state['country_code']}' not found. Cannot create default states.")
                        continue
                    if not existing:
                        orm_state = StateORM(
                            id=str(uuid4()),
                            country_id=country.id,
                            name=state["name"],
                            abbreviation=state["abbreviation"],
                            description=state["description"],
                        )
                        session.add(orm_state)
                        print(f"Inserted default state: {state['name']}")
                    else:
                        print(f"State '{state['name']}' already exists.")
        except Exception as error:
            print(f"Error creating default states: {error}")

    @staticmethod
    def _as_tuple(orm_state: StateORM) -> tuple:
        return (orm_state.id, orm_state.country_id, orm_state.name, orm_state.abbreviation, orm_state.description)
