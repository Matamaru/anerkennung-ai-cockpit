#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_data                 *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4
import json

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import DocumentData as DocumentDataORM
from backend.datamodule.sa import session_scope


class DocumentData(Model):
    def __init__(
            self, 
            ocr_doc_type_prediction: str = None, 
            ocr_predictions_str: str = None, 
            ocr_full_text: str = None, 
            ocr_extracted_data: dict = None, 
            ocr_source: str = None,
            check_ready: bool = False,
            validation_errors: dict = None,
            layoutlm_full_text: str = None,
            layout_lm_data: dict = None,
            review_status: str = None,
            review_comment: str = None,
            reviewed_by: str = None,
            reviewed_at = None,
            id: str = None):
        self.id = id or str(uuid4())
        self.ocr_doc_type_prediction_str = ocr_doc_type_prediction
        self.ocr_predictions_str = ocr_predictions_str
        self.ocr_full_text = ocr_full_text
        self.ocr_extracted_data = ocr_extracted_data
        self.ocr_source = ocr_source
        self.check_ready = check_ready
        self.validation_errors = validation_errors
        self.layoutlm_full_text = layoutlm_full_text
        self.layout_lm_data = layout_lm_data
        self.review_status = review_status
        self.review_comment = review_comment
        self.reviewed_by = reviewed_by
        self.reviewed_at = reviewed_at

    def insert(self) -> tuple:
        values = (
            self.id,
            self.ocr_doc_type_prediction_str,
            self.ocr_predictions_str,
            self.ocr_full_text,
            self.ocr_extracted_data,
            self.ocr_source,
            self.check_ready,
            self.validation_errors,
            self.layoutlm_full_text,
            self.layout_lm_data,
            self.review_status,
            self.review_comment,
            self.reviewed_by,
            self.reviewed_at,
        )
        try:
            with session_scope() as session:
                orm_dd = DocumentDataORM(
                    id=self.id,
                    ocr_doc_type_prediction_str=self.ocr_doc_type_prediction_str,
                    ocr_predictions_str=self.ocr_predictions_str,
                    ocr_full_text=self.ocr_full_text,
                    ocr_extracted_data=self.ocr_extracted_data,
                    ocr_source=self.ocr_source,
                    layoutlm_full_text=self.layoutlm_full_text,
                    layout_lm_data=self.layout_lm_data,
                    review_status=self.review_status,
                    review_comment=self.review_comment,
                    reviewed_by=self.reviewed_by,
                    reviewed_at=self.reviewed_at,
                )
                session.add(orm_dd)
                session.flush()
                return DocumentData._as_tuple(orm_dd)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_dd = session.query(DocumentDataORM).filter_by(id=values[10]).first()
                if not orm_dd:
                    raise UpdateError("Document data not found.")
                orm_dd.ocr_doc_type_prediction_str = values[0]
                orm_dd.ocr_predictions_str = values[1]
                orm_dd.ocr_full_text = values[2]
                orm_dd.ocr_extracted_data = values[3]
                orm_dd.ocr_source = values[4]
                orm_dd.check_ready = values[5]
                orm_dd.validation_errors = values[6]
                orm_dd.layoutlm_full_text = values[7]
                orm_dd.layout_lm_data = values[8]
                orm_dd.review_status = values[9]
                orm_dd.review_comment = values[10]
                orm_dd.reviewed_by = values[11]
                orm_dd.reviewed_at = values[12]
                session.flush()
                return DocumentData._as_tuple(orm_dd)
        except Exception as error:
            raise UpdateError(error)

    def delete(self, value: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_dd = session.query(DocumentDataORM).filter_by(id=value[0]).first()
                if not orm_dd:
                    raise DeleteError("Document data not found.")
                session.delete(orm_dd)
                return DocumentData._as_tuple(orm_dd)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(document_data_id: str) -> tuple:
        with session_scope() as session:
            orm_dd = session.query(DocumentDataORM).filter_by(id=document_data_id).first()
            return DocumentData._as_tuple(orm_dd) if orm_dd else None

    @staticmethod
    def get_all() -> list:
        with session_scope() as session:
            items = session.query(DocumentDataORM).all()
            return [DocumentData._as_tuple(i) for i in items]

    @staticmethod
    def from_tuple(tuple_data: tuple):
        if tuple_data:
            return DocumentData(
                id=tuple_data[0],
                ocr_doc_type_prediction=tuple_data[1],
                ocr_predictions_str=tuple_data[2],
                ocr_full_text=tuple_data[3],
                ocr_extracted_data=tuple_data[4],
                ocr_source=tuple_data[5],
                check_ready=tuple_data[6],
                validation_errors=tuple_data[7],
                layoutlm_full_text=tuple_data[8],
                layout_lm_data=tuple_data[9],
                review_status=tuple_data[10],
                review_comment=tuple_data[11],
                reviewed_by=tuple_data[12],
                reviewed_at=tuple_data[13],
            )
        return None

    @staticmethod
    def from_dict(data: dict):
        return DocumentData(
            ocr_doc_type_prediction=data.get("ocr_doc_type_prediction_str"),
            ocr_predictions_str=data.get("ocr_predictions_str"),
            ocr_full_text=data.get("ocr_full_text"),
            ocr_extracted_data=data.get("ocr_extracted_data"),
            layoutlm_full_text=data.get("layoutlm_full_text"),
            layout_lm_data=data.get("layout_lm_data"),
            review_status=data.get("review_status"),
            review_comment=data.get("review_comment"),
            reviewed_by=data.get("reviewed_by"),
            reviewed_at=data.get("reviewed_at"),
        )

    @staticmethod
    def _as_tuple(orm_dd: DocumentDataORM) -> tuple:
        return (
            orm_dd.id,
            orm_dd.ocr_doc_type_prediction_str,
            orm_dd.ocr_predictions_str,
            orm_dd.ocr_full_text,
            orm_dd.ocr_extracted_data,
            orm_dd.layoutlm_full_text,
            orm_dd.layout_lm_data,
            orm_dd.review_status,
            orm_dd.review_comment,
            orm_dd.reviewed_by,
            orm_dd.reviewed_at,
        )
