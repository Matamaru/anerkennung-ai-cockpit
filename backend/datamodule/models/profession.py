#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.profession                    *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.profession_sql import *
from backend.datamodule import db   

#=== Profession Model
class Profession(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Profession name={self.name}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.name, self.description)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_PROFESSION, values)
            tuple_profession = db.cursor.fetchone()

            if not tuple_profession:
                raise InsertError("Failed to insert profession into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_profession
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_PROFESSION, values)
            tuple_profession = db.cursor.fetchone()

            if not tuple_profession:
                raise UpdateError("Failed to update profession in database.")
            
            return tuple_profession

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)

        finally:
            db.close_conn()

    def delete(self) -> tuple:
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_PROFESSION, (self.id,))
            tuple_profession = db.cursor.fetchone()

            if not tuple_profession:
                raise DeleteError("Failed to delete profession from database.")
            
            return tuple_profession

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_id(profession_id: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_PROFESSION_BY_ID, (profession_id,))
            profession_tuple = db.cursor.fetchone()

            if not profession_tuple:
                return None
            
            return profession_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_name(name: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_PROFESSION_BY_NAME, (name,))
            profession_tuple = db.cursor.fetchone()

            if not profession_tuple:
                return None
            
            return profession_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_all() -> list:
        try:
            db.connect()
            # Execute select all
            db.cursor.execute(SELECT_ALL_PROFESSIONS)
            professions = db.cursor.fetchall()

            return professions
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def create_default_professions() -> bool:
        default_professions = [
            ("Nurse", "A healthcare professional who provides patient care and support."),
        ]
        try:
            db.connect()
            for prof in default_professions:
                # check if profession already exists
                db.cursor.execute(SELECT_PROFESSION_BY_NAME, (prof[0],))
                existing = db.cursor.fetchone()
                if existing:
                    print(f"Profession '{prof[0]}' already exists – skipping.")
                    continue  # skip existing professions
                prof_id = str(uuid4())
                values = (prof_id, prof[0], prof[1])
                # Execute insert
                db.cursor.execute(INSERT_PROFESSION, values)
                prof_tuple = db.cursor.fetchone()  # fetch to complete insert
                if prof_tuple:
                    print(f"Profession '{prof[0]}' created.")
                else:
                    print(f"Failed to create Profession '{prof[0]}'.")
            db.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating default professions: {error}")
            return False
        finally:
            db.close_conn()


    @staticmethod
    def from_tuple(prof_tuple: tuple):
        if not prof_tuple:
            return None
        profession = Profession(
            id=prof_tuple[0],
            name=prof_tuple[1],
            description=prof_tuple[2],
        )
        return profession
    
    @staticmethod
    def from_json(json_data: dict):
        if not json_data:
            return None
        profession = Profession(
            id=json_data.get("id"),
            name=json_data.get("name"),
            description=json_data.get("description"),
        )
        return profession