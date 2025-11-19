#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.role                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4

import psycopg2
from backend.datamodule.models.basemodel import InsertError, Model
from backend.datamodule.models.state_sql import *
from backend.datamodule import db

class State(Model):
    def __init__(self, id: str = None, name: str = None, abbreviation: str = None, description: str = None):
        if self.id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.name = name
        self.abbreviation = abbreviation
        self.description = description

    def __repr__(self):
        return f"<State name={self.name} abbreviation={self.abbreviation}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.name, self.abbreviation, self.description)
        # Check if state already exists
        exists, state_id = State.state_in_db(self.name)
        if exists:
            return False, state_id
        else:
            try:
                db.connect()
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
            
    def update(self):
        pass

    def delete(self):
        pass

    @staticmethod
    def get_by_id(state_id: str):
        pass

    @staticmethod
    def get_by_name(name: str):
        pass

    @staticmethod
    def get_by_abbreviation(abbreviation: str):
        pass

    @staticmethod
    def get_all():
        pass

    @staticmethod   
    def from_json(data: dict):
        return State(
            id=data.get("id"),
            name=data.get("name"),
            abbreviation=data.get("abbreviation"),
            description=data.get("description")
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        return State(
            id=data[0],
            name=data[1],
            abbreviation=data[2],
            description=data[3]
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

    