#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.status                        *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports    
from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.status_sql import *
from backend.datamodule import db   

#=== Status Model
class Status(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<Status id={self.id} name={self.name}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.name, self.description)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_STATUS, values)
            tuple_status = db.cursor.fetchone()

            if not tuple_status:
                raise InsertError("Failed to insert status into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_status
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_STATUS, values)
            tuple_status = db.cursor.fetchone()

            if not tuple_status:
                raise UpdateError("Failed to update status in database.")
            
            return tuple_status

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)

        finally:
            db.close_conn() 

    @staticmethod
    def create_default_statuses():
        """Create default statuses if they do not exist."""
        default_statuses = [
            {"name": "Uploaded", "description": "The document has been uploaded."},
            {"name": "Processing", "description": "The document is being processed."},
            {"name": "Reviewed", "description": "The document has been reviewed."},
            {"name": "Approved", "description": "The document has been approved."},
            {"name": "Rejected", "description": "The document has been rejected."}
        ]

        try:
            db.connect()
            for status in default_statuses:
                db.cursor.execute(SELECT_STATUS_BY_NAME, (status["name"],))
                result = db.cursor.fetchone()
                if not result:
                    new_status = Status(name=status["name"], description=status["description"])
                    db.cursor.execute(INSERT_STATUS, (new_status.id, new_status.name, new_status.description))
                    db.conn.commit()
                    print(f"Inserted default status: {status['name']}")
                else:
                    print(f"Status '{status['name']}' already exists.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating default statuses: {error}")
        finally:
            db.close_conn()

    @staticmethod
    def from_tuple(tuple_data: tuple):
        """
        Create a Status object from a tuple
        :param tuple_data: tuple of data
        :return: Status object
        """
        return Status(
            id=tuple_data[0],
            name=tuple_data[1],
            description=tuple_data[2]
        )
    
    @staticmethod
    def from_json(json_data: dict):
        """
        Create a Status object from a JSON dictionary
        :param json_data: dictionary of data
        :return: Status object
        """
        return Status(
            id=json_data.get("id"),
            name=json_data.get("name"),
            description=json_data.get("description")
        )   
    
    @staticmethod
    def get_by_id(status_id: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_STATUS_BY_ID, (status_id,))
            tuple_data = db.cursor.fetchone()   
            return tuple_data   
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()
        
    @staticmethod
    def get_all() -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_ALL_STATUS)
            tuples_status = db.cursor.fetchall()

            if not tuples_status:
                return None
            
            statuses = [Status.from_tuple(t) for t in tuples_status]
            return statuses
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_name(name: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_STATUS_BY_NAME, (name,))
            tuple_status = db.cursor.fetchone()

            if not tuple_status:
                return None
            
            return Status.from_tuple(tuple_status)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    