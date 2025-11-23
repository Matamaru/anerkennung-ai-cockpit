#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.role                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4

import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.country import Country
from backend.datamodule.models.country_sql import SELECT_COUNTRY_BY_CODE
from backend.datamodule.models.state_sql import *
from backend.datamodule import db

class State(Model):
    def __init__(self, 
                 id: str = None, 
                 country_id: str = None, 
                 name: str = None, 
                 abbreviation: str = None, 
                 description: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.country_id = country_id
        self.name = name
        self.abbreviation = abbreviation
        self.description = description

    def __repr__(self):
        return f"<State name={self.name} abbreviation={self.abbreviation}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.country_id, self.name, self.abbreviation, self.description)
        try:
            db.connect()
            # check if state with same name already exists
            db.cursor.execute(SELECT_STATE_BY_NAME, (self.name,))
            existing_state = db.cursor.fetchone()
            if existing_state:
                raise InsertError(f"State with name '{self.name}' already exists in database.")
                return None

            # Execute insert
            db.cursor.execute(INSERT_STATE, values)
            tuple_state = db.cursor.fetchone()

            if not tuple_state:
                raise InsertError("Failed to insert state into database.")
            
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_state
            
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_STATE, values)
            tuple_state = db.cursor.fetchone()

            if not tuple_state:
                raise UpdateError("Failed to update state in database.")
            
        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)
        finally:
            db.close_conn()
            return tuple_state

    def delete(self):
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_STATE, (self.id,))
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)
        finally:
            db.close_conn()
            return self.id
        
    @staticmethod
    def get_by_id(state_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_STATE_BY_ID, (state_id,))
            tuple_state = db.cursor.fetchone()

            if not tuple_state:
                return None
            
            return State.from_tuple(tuple_state)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_name(name: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_STATE_BY_NAME, (name,))
            tuple_state = db.cursor.fetchone()

            if not tuple_state:
                return None
            
            return State.from_tuple(tuple_state)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_code(code: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_STATE_BY_ABBREVIATION, (code,))
            tuple_state = db.cursor.fetchone()

            if not tuple_state:
                return None
            
            return State.from_tuple(tuple_state)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_all():
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_ALL_STATES)
            tuples_states = db.cursor.fetchall()

            states = [State.from_tuple(t) for t in tuples_states]
            return states
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

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
    def from_tuple(data: tuple):
        return State(
            id=data[0],
            country_id=data[1],
            name=data[2],
            abbreviation=data[3],
            description=data[4]
        )

    @staticmethod
    def state_in_db(name: str):
        """
        Check if state with given name exists in db
        :param name: name of state
        :return: (bool, State-ID or None)
        """
        state = State.select_where_column_equals(
            sql_select_model = SELECT_ALL_STATES, 
            column = 'name', 
            value = name)
        if state:
            return True, state[0]
        else:
            return False, None
        
    @staticmethod
    def create_default_states():
        """
        Create default states in db
        :return: None
        """

        # set of default states
        # ISO 3166-2:DE
        default_states = [
            {
               "name": "Bayern",
               "abbreviation": "DE-BY",
               "description": "Bavaria",
               "country_code": "DE"
           },
           {
               "name": "Berlin",
               "abbreviation": "DE-BE",
               "description": "Berlin",
               "country_code": "DE"
           },
           {
               "name": "Nordrhein-Westfalen",
               "abbreviation": "DE-NW",
               "description": "North Rhine-Westphalia",
               "country_code": "DE"
           }
        ]
 
#        print(f"States: {default_states}")

        try:
            db.connect()
            for state in default_states:
#                print(f"Processing state: {state['name']}")
                # Check if state already exists
                values = (state["name"],)
                db.cursor.execute(SELECT_STATE_BY_NAME, values)
                tuple_state = db.cursor.fetchone()

                # Get country id for country code 'DE'
                country_code = state["country_code"]    
                try:
                    db.cursor.execute(SELECT_COUNTRY_BY_CODE, (country_code,))
                    country_tuple = db.cursor.fetchone()
                    if country_tuple:
                        country_id = country_tuple[0]
                        #print(f"Country ID for '{country_code}': {country_id}")
                    else:
                        print(f"Country with code '{country_code}' not found. Cannot create default states.")
                except Exception as e:
                        print(f"Error retrieving country with code '{country_code}': {e}")
                
                # Insert state if it does not exist
                if not tuple_state:
                    new_state = State(
                        id=str(uuid4()),
                        country_id=country_id,
                        name=state["name"],
                        abbreviation=state["abbreviation"],
                        description=state["description"]
                    )
                    values = (new_state.id, new_state.country_id, new_state.name, new_state.abbreviation, new_state.description)
                    db.cursor.execute(INSERT_STATE, values)
                    print(f"Inserted default state: {state['name']}")
                else:
                    print(f"State '{state['name']}' already exists.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating default states: {error}")
        finally:
            db.close_conn()
