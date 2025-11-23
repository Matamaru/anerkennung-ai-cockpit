#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.file_type                     *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from curses import error
from uuid import uuid4
import psycopg2
from backend.datamodule.models import status
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.file_type_sql import *
from backend.datamodule import db   

#=== File Type Model
class FileType(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<FileType name={self.name}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.name, self.description)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_FILE_TYPE, values)
            tuple_file_type = db.cursor.fetchone()

            if not tuple_file_type:
                raise InsertError("Failed to insert file type into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_file_type
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_FILE_TYPE, values)
            tuple_file_type = db.cursor.fetchone()

            if not tuple_file_type:
                raise UpdateError("Failed to update file type in database.")
            
            return tuple_file_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)
        
        finally:
            db.close_conn() 

    def delete(self) -> tuple:
        values = (self.id, )
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_FILE_TYPE, values)
            tuple_file_type = db.cursor.fetchone()

            if not tuple_file_type:
                raise DeleteError("Failed to delete file type from database.")
            
            return tuple_file_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()
        
    @staticmethod
    def from_tuple(tuple_data: tuple):
        return FileType(
            id=tuple_data[0],
            name=tuple_data[1],
            description=tuple_data[2]
        )
    
    @staticmethod
    def from_json(json_data: dict):
        return FileType(
            id=json_data.get("id"),
            name=json_data.get("name"),
            description=json_data.get("description")
        )
    
    @staticmethod
    def get_by_id(file_type_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_FILE_TYPE_BY_ID, (file_type_id,))
            tuple_file_type = db.cursor.fetchone()

            if not tuple_file_type:
                raise RecordNotFoundError("File type not found in database.")
            
            return tuple_file_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_name(name: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_FILE_TYPE_BY_NAME, (name,))
            tuple_file_type = db.cursor.fetchone()

            if not tuple_file_type:
                raise RecordNotFoundError("File type not found in database.")
            
            return tuple_file_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_all() -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_ALL_FILE_TYPES)
            tuples_file_types = db.cursor.fetchall()

            if not tuples_file_types:
                return None
            
            file_types = [FileType.from_tuple(t) for t in tuples_file_types]
            return file_types
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def create_default_file_types():
        default_file_types = [
            {"name": "PDF",  "description": "PDF Document"},
            {"name": "DOCX", "description": "Word Document"},
            {"name": "JPEG", "description": "JPEG Image"},
            {"name": "PNG",  "description": "PNG Image"}
        ]

        try:
            db.connect()

            for file_type in default_file_types:

                db.cursor.execute(SELECT_FILE_TYPE_BY_NAME, (file_type["name"],))
                result = db.cursor.fetchone()

                if not result:
                    new_file_type = FileType(
                        name=file_type["name"],
                        description=file_type["description"]
                    )

                    db.cursor.execute(
                        INSERT_FILE_TYPE,
                        (new_file_type.id, new_file_type.name, new_file_type.description)
                    )
                    print(f"Inserted default file type: {file_type['name']}")
                else:
                    print(f"File type '{file_type['name']}' already exists.")

            db.conn.commit()

        except (Exception, psycopg2.DatabaseError) as error:
            db.conn.rollback()
            print(f"Error creating default file types: {error}")
        finally:
            db.close_conn()
