#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_sql                  *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_DOCUMENT = """
CREATE TABLE IF NOT EXISTS _documents (
    id VARCHAR(36) PRIMARY KEY,
    file_id VARCHAR(36),
    document_type_id VARCHAR(36),
    document_data_id VARCHAR(36),
    user_id VARCHAR(36),
    status_id VARCHAR(36),
    last_modified TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (file_id) REFERENCES _files(id),
    FOREIGN KEY (document_type_id) REFERENCES _document_types(id),
    FOREIGN KEY (document_data_id) REFERENCES _document_datas(id),
    FOREIGN KEY (user_id) REFERENCES _users(user_id),
    FOREIGN KEY (status_id) REFERENCES _statuses(id)
);
"""

DROP_TABLE_DOCUMENT = """
DROP TABLE IF EXISTS _documents;
"""

INSERT_DOCUMENT = """
INSERT INTO _documents (id, file_id, document_type_id, document_data_id, user_id, status_id, last_modified)
VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING *
"""

UPDATE_DOCUMENT = """
UPDATE _documents
SET file_id = %s, document_type_id = %s, document_data_id = %s, user_id = %s, status_id = %s, last_modified = %s
WHERE id = %s       
RETURNING *;
"""

DELETE_DOCUMENT = """
DELETE FROM _documents
WHERE id = %s
RETURNING *;
""" 

SELECT_DOCUMENT_BY_ID = """
SELECT *
FROM _documents
WHERE id = %s;
""" 

SELECT_ALL_DOCUMENTS = """
SELECT *
FROM _documents
"""

SELECT_DOCUMENTS_BY_USER_ID = """
SELECT *
FROM _documents
WHERE user_id = %s;
"""

SELECT_DOCUMENTS_BY_STATUS_ID = """
SELECT *
FROM _documents
WHERE status_id = %s;
"""

SELECT_DOCUMENTS_BY_TYPE_ID = """
SELECT *
FROM _documents
WHERE document_type_id = %s;
"""

SELECT_DOCUMENTS_BY_FILE_ID = """
SELECT *
FROM _documents
WHERE file_id = %s;
"""

SELECT_BY_STATUS_AND_USER_ID = """
SELECT *
FROM _documents
WHERE status_id = %s AND user_id = %s;
""" 
