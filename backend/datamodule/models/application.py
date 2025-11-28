#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.application                   *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.application_sql import *
from backend.datamodule import db   

#=== Application Model
class Application(Model):
    def __init__(self, user_id: str = None, profession_id: str = None, country_id: str = None, state_id: str = None, id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.user_id = user_id
        self.profession_id = profession_id
        self.country_id = country_id
        self.state_id = state_id

    def __repr__(self):
        return f"<Application id={self.id} user_id={self.user_id} profession_id={self.profession_id} country_id={self.country_id} state_id={self.state_id}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.user_id, self.profession_id, self.country_id, self.state_id)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_APPLICATION, values)
            tuple_application = db.cursor.fetchone()

            if not tuple_application:
                raise InsertError("Failed to insert application into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_application


    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_APPLICATION, values)
            tuple_application = db.cursor.fetchone()

            if not tuple_application:
                raise UpdateError("Failed to update application in database.")
            
            return tuple_application

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)
        
        finally:
            db.close_conn()

    def delete(self) -> tuple:
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_APPLICATION, (self.id,))
            tuple_application = db.cursor.fetchone()

            if not tuple_application:
                raise DeleteError("Failed to delete application from database.")
            
            return tuple_application

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_all() -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_ALL_APPLICATIONS)
            applications = db.cursor.fetchall()

            return applications

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_id(application_id: str) -> tuple:
        try:
            db.connect()
            # Execute select by id
            db.cursor.execute(SELECT_APPLICATION_BY_ID, (application_id,))
            tuple_application = db.cursor.fetchone()

            return tuple_application

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_profession_id(profession_id: str) -> list:
        try:
            db.connect()
            # Execute select by profession id
            db.cursor.execute(SELECT_APPLICATIONS_BY_PROFESSION_ID, (profession_id,))
            applications = db.cursor.fetchall()

            return applications

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_country_id(country_id: str) -> list:
        try:
            db.connect()
            # Execute select by country id
            db.cursor.execute(SELECT_APPLICATIONS_BY_COUNTRY_ID, (country_id,))
            applications = db.cursor.fetchall()

            return applications

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_state_id(state_id: str) -> list:
        try:
            db.connect()
            # Execute select by state id
            db.cursor.execute(SELECT_APPLICATIONS_BY_STATE_ID, (state_id,))
            applications = db.cursor.fetchall()

            return applications

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_user_id(user_id: str) -> list:
        try:
            db.connect()
            # Execute select by user id
            db.cursor.execute(SELECT_APPLICATIONS_BY_USER_ID, (user_id,))
            applications = db.cursor.fetchall()

            return applications

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            db.close_conn()

    @staticmethod   
    def from_tuple(t: tuple):
        return Application(
            id=t[0],
            user_id=t[1],
            profession_id=t[2],
            country_id=t[3],
            state_id=t[4]
        )
    
    @staticmethod
    def from_json(data: dict):
        return Application(
            id=data.get("id"),
            user_id=data.get("user_id"),
            profession_id=data.get("profession_id"),
            country_id=data.get("country_id"),
            state_id=data.get("state_id")
        )