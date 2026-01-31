#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_data_sql             *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_DOCUMENT_DATA = """
CREATE TABLE IF NOT EXISTS _document_datas (
    id VARCHAR(36) PRIMARY KEY,
    ocr_doc_type_prediction_str TEXT,
    ocr_predictions_str TEXT,
    ocr_full_text TEXT,
    ocr_extracted_data JSONB,
    layoutlm_full_text TEXT,
    layout_lm_data JSONB,
    review_status TEXT,
    review_comment TEXT,
    reviewed_by VARCHAR(36),
    reviewed_at TIMESTAMP
);
"""

DROP_TABLE_DOCUMENT_DATA = """
DROP TABLE IF EXISTS _document_datas;
"""

INSERT_DOCUMENT_DATA = """
INSERT INTO _document_datas (id, ocr_doc_type_prediction_str, ocr_predictions_str, ocr_full_text, ocr_extracted_data, layoutlm_full_text, layout_lm_data, review_status, review_comment, reviewed_by, reviewed_at)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING *
"""

UPDATE_DOCUMENT_DATA = """
UPDATE _document_datas  
SET ocr_doc_type_prediction_str = %s, ocr_predictions_str = %s, ocr_full_text = %s, ocr_extracted_data = %s, layoutlm_full_text = %s, layout_lm_data = %s, review_status = %s, review_comment = %s, reviewed_by = %s, reviewed_at = %s
WHERE id = %s
RETURNING *;
""" 

DELETE_DOCUMENT_DATA = """
DELETE FROM _document_datas
WHERE id = %s
RETURNING *;
""" 

SELECT_DOCUMENT_DATA_BY_ID = """
SELECT id, ocr_doc_type_prediction_str, ocr_predictions_str, ocr_full_text, ocr_extracted_data, layoutlm_full_text, layout_lm_data, review_status, review_comment, reviewed_by, reviewed_at
FROM _document_datas
WHERE id = %s;
"""

SELECT_ALL_DOCUMENT_DATA = """
SELECT *
FROM _document_datas
""" 
