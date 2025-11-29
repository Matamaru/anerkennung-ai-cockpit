#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.app_docs_sql                  *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_APP_DOCS = """
CREATE TABLE IF NOT EXISTS _app_docs (
    id varchar(36) PRIMARY KEY,
    application_id varchar(36) NOT NULL,
    document_id varchar(36),
    requirements_id varchar(36) NOT NULL,
    FOREIGN KEY (application_id) REFERENCES _applications(id),
    FOREIGN KEY (document_id) REFERENCES _documents(id),
    FOREIGN KEY (requirements_id) REFERENCES _requirements(id)
);
"""

DROP_TABLE_APP_DOCS = """
DROP TABLE IF EXISTS _app_docs;
"""

INSERT_APP_DOCS = """
INSERT INTO _app_docs (id, application_id, document_id, requirements_id)
VALUES (%s, %s, %s, %s)
RETURNING *;
"""

UPDATE_APP_DOCS = """
UPDATE _app_docs  
SET application_id = %s, document_id = %s, requirements_id = %s
WHERE id = %s
RETURNING *;
"""

DELETE_APP_DOCS = """
DELETE FROM _app_docs
WHERE id = %s
RETURNING *;
"""

SELECT_APP_DOCS_BY_ID = """
SELECT id, application_id, document_id, requirements_id
FROM _app_docs
WHERE id = %s;
"""

SELECT_ALL_APP_DOCS = """
SELECT *
FROM _app_docs
"""

SELECT_APP_DOCS_BY_APPLICATION_ID = """
SELECT id, application_id, document_id, requirements_id
FROM _app_docs
WHERE application_id = %s;
"""

SELECT_APP_DOCS_BY_DOCUMENT_ID = """
SELECT id, application_id, document_id, requirements_id
FROM _app_docs
WHERE document_id = %s;
"""

SELECT_APP_DOCS_BY_REQUIREMENTS_ID = """
SELECT id, application_id, document_id, requirements_id
FROM _app_docs
WHERE requirements_id = %s;
"""

#TODO: Optimize query with JOINs
SELECT_DOCS_FOR_APPLICATION = """
SELECT 
        d.id AS document_id, 
        f.id AS file_id,
        d.document_type_id, 
        ft.id AS file_type_id,
        dd.id AS document_data_id,
        dt.name AS document_type_name, 
        d.last_modified, 
        d.status_id,
        st.name AS status_name,
        f.filename,
        f.filepath,
        f.filetype,
        u.id AS user_id,
        doc_data.ocr_full_text
    FROM _app_docs ad
    JOIN _documents d ON ad.document_id = d.id
    JOIN _document_types dt ON d.document_type_id = dt.id
    JOIN _files f ON d.file_id = f.id
    JOIN _document_datas doc_data ON d.document_data_id = doc_data.id
    JOIN _file_types ft ON f.file_type_id = ft.id
    JOIN _statuses st ON d.status_id = st.id
    JOIN _users u ON d.user_id = u.id
    WHERE ad.application_id = %s
    """