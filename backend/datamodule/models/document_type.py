#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_type                 *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.document_type_sql import *
from backend.datamodule import db   

#=== Document Type Model

class DocumentType(Model):
    def __init__(self, name: str = None, description: str = None, id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.name = name
        self.description = description

    def __repr__(self):
        return f"<DocumentType name={self.name}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.name, self.description)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_DOCUMENT_TYPE, values)
            tuple_document_type = db.cursor.fetchone()

            if not tuple_document_type:
                raise InsertError("Failed to insert document type into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_document_type
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_DOCUMENT_TYPE, values)
            tuple_document_type = db.cursor.fetchone()

            if not tuple_document_type:
                raise UpdateError("Failed to update document type in database.")
            
            return tuple_document_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)

        finally:
            db.close_conn()
    
    def delete(self) -> tuple:
        values = (self.id,)
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_DOCUMENT_TYPE, values)
            tuple_document_type = db.cursor.fetchone()

            if not tuple_document_type:
                raise DeleteError("Failed to delete document type from database.")
            
            return tuple_document_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_id(id: str) -> tuple:
        try:
            db.connect()
            # Execute select by id
            db.cursor.execute(SELECT_DOCUMENT_TYPE_BY_ID, (id,))
            tuple_document_type = db.cursor.fetchone()

            return tuple_document_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_name(name: str) -> tuple:
        try:
            db.connect()
            # Execute select by name
            db.cursor.execute(SELECT_DOCUMENT_TYPE_BY_NAME, (name,))
            tuple_document_type = db.cursor.fetchone()

            return tuple_document_type

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_all() -> tuple:
        try:
            db.connect()
            # Execute select all
            db.cursor.execute(SELECT_ALL_DOCUMENT_TYPES)
            tuples_document_types = db.cursor.fetchall()

            return tuples_document_types

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn()

    @staticmethod   
    def from_tuple(t: tuple):
        return DocumentType(
            id=t[0],
            name=t[1],
            description=t[2]
        )

    @staticmethod
    def from_json(json_data: str):
        data = json.loads(json_data)
        return DocumentType(
            id=data.get("id"),
            name=data.get("name"),
            description=data.get("description")
        ) 

    @staticmethod
    def create_default_document_types() -> tuple:
        # default document types like ID, degree certificate, etc.
        default_types = [
            ("ID Card", "Official identification card issued by the government."),
            ("Degree Certificate", "Certificate awarded upon completion of a degree program."),
            ("Transcript", "Official record of a student's academic performance."),
            ("CV", "Curriculum Vitae detailing an individual's education and work experience."),
            ("Resume", "Document summarizing an individual's education, work experience, and skills."),
            ("Cover Letter", "Letter sent with a resume to provide additional information about the applicant.")
        ]
        try:
            db.connect()
            for doc_type in default_types:
                # check if document type already exists
                try:
                    db.cursor.execute(SELECT_DOCUMENT_TYPE_BY_NAME, (doc_type[0],))
                    existing = db.cursor.fetchone()
                except (Exception, psycopg2.DatabaseError) as error:
                    existing = None
                if existing:
                    print(f"Document type '{doc_type[0]}' already exists – skipping.")
                    continue  # skip existing types
                    # insert new document type                      
                doc_type_id = str(uuid4())
                values = (doc_type_id, doc_type[0], doc_type[1])
                # Execute insert
                db.cursor.execute(INSERT_DOCUMENT_TYPE, values)
                doc_tuple = db.cursor.fetchone()  # fetch to complete insert
                if doc_tuple:
                    print(f"DocumentType '{doc_type[0]}' created.")
                else:
                    print(f"Failed to create DocumentType '{doc_type[0]}'.")
            db.conn.commit()
            return True
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating default document types: {error}")
            return False
        finally:
            db.close_conn()        