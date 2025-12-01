#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_data                 *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.document_data_sql import *
from backend.datamodule import db
import psycopg2 

#=== Document Data Model

class DocumentData(Model):
    def __init__(self, 
                 id: str = None, 
                 ocr_doc_type_prediction: str = None, 
                 ocr_predictions_str: str = None, 
                 ocr_full_text: str = None, 
                 ocr_extracted_data: dict = None, 
                 layoutlm_full_text: str = None, 
                 layout_lm_data: dict = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.ocr_doc_type_prediction_str = ocr_doc_type_prediction
        self.ocr_predictions_str = ocr_predictions_str
        self.ocr_full_text = ocr_full_text
        self.ocr_extracted_data = ocr_extracted_data
        self.layoutlm_full_text = layoutlm_full_text
        self.layout_lm_data = layout_lm_data

    def __repr__(self):
        return f"<DocumentData id={self.id}>"
    
    def insert(self) -> tuple:
        values = (
            self.id,
            self.ocr_doc_type_prediction_str,
            self.ocr_predictions_str,
            self.ocr_full_text,
            json.dumps(self.ocr_extracted_data) if self.ocr_extracted_data else None,
            self.layoutlm_full_text,
            json.dumps(self.layout_lm_data) if self.layout_lm_data else None
        )
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_DOCUMENT_DATA, values)
            tuple_document_data = db.cursor.fetchone()

            if tuple_document_data:
                return tuple_document_data
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_DOCUMENT_DATA, values)
            tuple_document_data = db.cursor.fetchone()

            if not tuple_document_data:
                raise UpdateError("Failed to update document data in database.")
            
            return tuple_document_data

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)

        finally:
            db.close_conn()

    def delete(self) -> tuple:
        value = (self.id,)
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_DOCUMENT_DATA, value)
            tuple_document_data = db.cursor.fetchone()

            if not tuple_document_data:
                raise DeleteError("Failed to delete document data from database.")
            
            return self.id

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def from_tuple(tuple_data: tuple):
        """
        Create a DocumentData object from a tuple
        :param tuple_data: tuple of data
        :return: DocumentData object
        """
        if tuple_data:
            return DocumentData(
                id=tuple_data[0],
                ocr_doc_type_prediction_str=tuple_data[1],
                ocr_predictions_str=tuple_data[2],
                ocr_full_text=tuple_data[3],
                ocr_extracted_data=tuple_data[4],
                layoutlm_full_text=tuple_data[5],
                layout_lm_data=tuple_data[6]
            )
        else:
            return None

    @staticmethod
    def from_json(json_data: str):
        """
        Create a DocumentData object from a json
        :param json_data: json of data
        :return: DocumentData object
        """
        data = json.loads(json_data)
        return DocumentData(
            id=data.get("id"),
            ocr_doc_type_prediction_str=data.get("ocr_doc_type_prediction_str"),
            ocr_predictions_str=data.get("ocr_predictions_str"),
            ocr_full_text=data.get("ocr_full_text"),
            ocr_extracted_data=data.get("ocr_extracted_data"),
            layoutlm_full_text=data.get("layoutlm_full_text"),
            layout_lm_data=data.get("layout_lm_data")
        )
    
    @staticmethod
    def get_by_id(document_data_id: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_DOCUMENT_DATA_BY_ID, (document_data_id,))
            tuple_document_data = db.cursor.fetchone()

            if not tuple_document_data:
                return None
            
            return DocumentData.from_tuple(tuple_document_data)
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_all() -> tuple:
        try:
            db.connect()
            # Execute select all
            db.cursor.execute(SELECT_ALL_DOCUMENT_DATA)
            tuples_document_data = db.cursor.fetchall()

            return tuples_document_data

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            db.close_conn()

    