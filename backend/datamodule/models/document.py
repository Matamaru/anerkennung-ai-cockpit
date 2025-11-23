#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document                      *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.document_sql import *
from backend.datamodule import db   

#=== Document Model
class Document(Model):
    def __init__(
            self, 
            file_id: str = None, 
            document_type_id: str = None, 
            document_data_id: str = None, 
            user_id: str = None, 
            status_id: str = None, 
            id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.file_id = file_id
        self.document_type_id = document_type_id
        self.document_data_id = document_data_id
        self.user_id = user_id
        self.status_id = status_id

    def __repr__(self):
        return f"<Document id={self.id} file_id={self.file_id} document_type_id={self.document_type_id}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.file_id, self.document_type_id, self.document_data_id, self.user_id, self.status_id, )
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_DOCUMENT, values)
            tuple_document = db.cursor.fetchone()

            if not tuple_document:
                raise InsertError("Failed to insert document into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_document
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_DOCUMENT, values)
            tuple_document = db.cursor.fetchone()

            if not tuple_document:
                raise UpdateError("Failed to update document in database.")
            
            return tuple_document

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)

        finally:
            db.close_conn()

    def delete(self) -> tuple:
        value = (self.id,)
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_DOCUMENT, value)
            tuple_document = db.cursor.fetchone()

            if not tuple_document:
                raise DeleteError("Failed to delete document from database.")
            
            return tuple_document

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def from_tuple(tuple_data: tuple):
        """
        Create a Document object from a tuple
        :param tuple_data: tuple of data
        :return: Document object
        """
        return Document(
            id=tuple_data[0],
            file_id=tuple_data[1],
            document_type_id=tuple_data[2],
            document_data_id=tuple_data[3],
            user_id=tuple_data[4],
            status_id=tuple_data[5]
        )
    
    @staticmethod
    def from_json(json_data: dict):
        """
        Create a Document object from a json
        :param json_data: json of data
        :return: Document object
        """
        return Document(
            id=json_data.get("id"),
            file_id=json_data.get("file_id"),
            document_type_id=json_data.get("document_type_id"),
            document_data_id=json_data.get("document_data_id"),
            user_id=json_data.get("user_id"),
            status_id=json_data.get("status_id")
        )   
    
    @staticmethod
    def get_by_id(document_id: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_DOCUMENT_BY_ID, (document_id,))
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
            db.cursor.execute(SELECT_ALL_DOCUMENTS)
            tuples = db.cursor.fetchall()   
            return tuples   
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_user_id(user_id: str) -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_DOCUMENTS_BY_USER_ID, (user_id,))
            tuples = db.cursor.fetchall()   
            return tuples   
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_status_id(status_id: str) -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_DOCUMENTS_BY_STATUS_ID, (status_id,))
            tuples = db.cursor.fetchall()   
            return tuples   
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_type_id(document_type_id: str) -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_DOCUMENTS_BY_TYPE_ID, (document_type_id,))
            tuples = db.cursor.fetchall()   
            return tuples   
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_file_id(file_id: str) -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_DOCUMENTS_BY_FILE_ID, (file_id,))
            tuples = db.cursor.fetchall()   
            return tuples   
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_status_and_user_id(status_id: str, user_id: str) -> list:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_BY_STATUS_AND_USER_ID, (status_id, user_id))
            tuples = db.cursor.fetchall()   
            return tuples   
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()