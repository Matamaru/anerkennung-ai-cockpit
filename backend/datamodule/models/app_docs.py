#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.app_docs                       *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4
import psycopg2
from backend.datamodule.datamodule import db
from backend.datamodule.models.app_docs_sql import *
from backend.datamodule.models.application import Application
from backend.datamodule.models.document import Document
from backend.datamodule.models.requirements import Requirements
from backend.datamodule.models.basemodel import *

#=== AppDocs Model  
class AppDocs(Model):
    def __init__(self, id: str, application_id: str, document_id: str, requirements_id: str):
        self.id = id
        self.application_id = application_id
        self.document_id = document_id
        self.requirements_id = requirements_id

    def insert(self):
        values = (self.id, self.application_id, self.document_id, self.requirements_id)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_APP_DOCS, values)
            tuple_app_docs = db.cursor.fetchone()
            if not tuple_app_docs:
                raise InsertError("Failed to insert AppDocs into database.")
            return tuple_app_docs
            
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)
        finally:
            db.close()

    def update(self, values: tuple):
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_APP_DOCS, values)
            tuple_app_docs = db.cursor.fetchone()
            if not tuple_app_docs:
                raise UpdateError("Failed to update AppDocs in database.")
            return tuple_app_docs

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)
        finally:
            db.close()

    def delete(self):
        values = (self.id,)
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_APP_DOCS, values)
            tuple_app_docs = db.cursor.fetchone()
            if not tuple_app_docs:
                raise DeleteError("Failed to delete AppDocs from database.")
            return tuple_app_docs

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)
        finally:
            db.close()

    @staticmethod
    def from_tuple(tuple_app_docs):
        if not tuple_app_docs:
            return None
        return AppDocs(
            id=tuple_app_docs[0],
            application_id=tuple_app_docs[1],
            document_id=tuple_app_docs[2],
            requirements_id=tuple_app_docs[3]
        )
    
    @staticmethod
    def from_json(json_app_docs):
        if not json_app_docs:
            return None
        return AppDocs(
            id=json_app_docs.get("id", str(uuid4())),
            application_id=json_app_docs["application_id"],
            document_id=json_app_docs["document_id"],
            requirements_id=json_app_docs["requirements_id"]
        )
    
    @staticmethod
    def get_by_id(app_docs_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_APP_DOCS_BY_ID, (app_docs_id,))
            app_docs_tuple = db.cursor.fetchone()
            if not app_docs_tuple:
                return None
            return app_docs_tuple

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)
        finally:
            db.close()

    @staticmethod
    def get_all():
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_ALL_APP_DOCS)
            app_docs_tuples = db.cursor.fetchall()
            return app_docs_tuples

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)
        finally:
            db.close()

    @staticmethod
    def get_by_application_id(application_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_APP_DOCS_BY_APPLICATION_ID, (application_id,))
            app_docs_tuples = db.cursor.fetchall()
            return app_docs_tuples

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)
        finally:
            db.close()

    @staticmethod
    def get_by_document_id(document_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_APP_DOCS_BY_DOCUMENT_ID, (document_id,))
            app_docs_tuples = db.cursor.fetchall()
            return app_docs_tuples

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)
        finally:
            db.close()

    @staticmethod
    def get_by_requirements_id(requirements_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_APP_DOCS_BY_REQUIREMENTS_ID, (requirements_id,))
            app_docs_tuples = db.cursor.fetchall()
            return app_docs_tuples

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)
        finally:
            db.close()

    @staticmethod
    def get_docs_for_application(application_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_DOCS_FOR_APPLICATION, (application_id,))
            docs_tuples = db.cursor.fetchall()
            return docs_tuples

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)
        finally:
            db.close()