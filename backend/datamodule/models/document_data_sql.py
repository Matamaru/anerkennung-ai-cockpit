#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_data_sql             *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_DOCUMENT_DATA = """
CREATE TABLE IF NOT EXISTS _document_datas (
    id VARCHAR(36) PRIMARY KEY,
    ocr_full_text TEXT,
    ocr_extracted_data JSONB,
    layoutlm_full_text TEXT,
    layout_lm_data JSONB
);
"""

DROP_TABLE_DOCUMENT_DATA = """
DROP TABLE IF EXISTS _document_datas;
"""

INSERT_DOCUMENT_DATA = """
INSERT INTO _document_datas (id, ocr_full_text, ocr_extracted_data, layoutlm_full_text, layout_lm_data)
VALUES (%s, %s, %s, %s, %s)
RETURNING *
"""

UPDATE_DOCUMENT_DATA = """
UPDATE _document_datas  
SET ocr_full_text = %s, ocr_extracted_data = %s, layoutlm_full_text = %s, layout_lm_data = %s
WHERE id = %s
RETURNING *;
""" 

DELETE_DOCUMENT_DATA = """
DELETE FROM _document_datas
WHERE id = %s
RETURNING *;
""" 

SELECT_DOCUMENT_DATA_BY_ID = """
SELECT id, ocr_full_text, ocr_extracted_data, layoutlm_full_text, layout_lm_data
FROM _document_datas
WHERE id = %s;
"""

SELECT_ALL_DOCUMENT_DATA = """
SELECT *
FROM _document_datas
""" 


