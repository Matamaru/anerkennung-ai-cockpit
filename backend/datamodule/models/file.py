#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.file                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.file_sql import *
from backend.datamodule import db   

#=== File Model
class File(Model):
    def __init__(self, filename: str = None, filepath: str = None, filetype_id: str = None, id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.filename = filename
        self.filepath = filepath
        self.filetype_id = filetype_id

    def __repr__(self):
        return f"<File filename={self.filename} filetype_id={self.filetype_id}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.filename, self.filepath, self.filetype_id)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_FILE, values)
            tuple_file = db.cursor.fetchone()

            if not tuple_file:
                raise InsertError("Failed to insert file into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_file
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_FILE, values)
            tuple_file = db.cursor.fetchone()

            if not tuple_file:
                raise UpdateError("Failed to update file in database.")
            
            return tuple_file

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)

        finally:
            db.close_conn()

    def delete(self, value: tuple) -> int:
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_FILE, value)
            return value[0]

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def from_tuple(tuple_data: tuple):
        """
        Create a File object from a tuple
        :param tuple_data: tuple of data
        :return: File object
        """
        if tuple_data:
            return File(
                id=tuple_data[0],
                filename=tuple_data[1],
                filepath=tuple_data[2],
                filetype_id=tuple_data[3]
            )
        return None


    @staticmethod
    def from_json(json_data: dict):
        """
        Create a File object from a json
        :param json_data: json of data
        :return: File object
        """
        if json_data:
            return File(
                id=json_data.get("id"),
                filename=json_data.get("filename"),
                filepath=json_data.get("filepath"),
                filetype_id=json_data.get("filetype_id")
            )
        return None
        
    @staticmethod
    def get_by_id(id: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_FILE_BY_ID, (id,))
            tuple_data = db.cursor.fetchone()
            return tuple_data
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_name(filename: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_FILE_BY_NAME, (filename,))
            tuple_data = db.cursor.fetchone()
            return tuple_data
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_all() -> tuple:
        try:
            db.connect()
            # Execute select all
            db.cursor.execute(SELECT_ALL_FILES)
            tuples_data = db.cursor.fetchall()
            return tuples_data
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn() 

    @staticmethod
    def get_all_by_filetype_name(filetype_name: str) -> tuple:
        try:
            db.connect()
            # Execute select all
            db.cursor.execute(SELECT_ALL_FILES_BY_FILETYPE_NAME, (filetype_name,))
            tuples_data = db.cursor.fetchall()
            return tuples_data
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()