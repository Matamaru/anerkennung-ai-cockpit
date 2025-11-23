#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.document_type_sql             *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_DOCUMENT_TYPE = """
CREATE TABLE IF NOT EXISTS _document_types (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);
"""

DROP_TABLE_DOCUMENT_TYPE = """
DROP TABLE IF EXISTS _document_types;
"""     

INSERT_DOCUMENT_TYPE = """
INSERT INTO _document_types (id, name, description)
VALUES (%s, %s, %s)
RETURNING *
"""

UPDATE_DOCUMENT_TYPE = """
UPDATE _document_types
SET name = %s, description = %s
WHERE id = %s
RETURNING *;
""" 

DELETE_DOCUMENT_TYPE = """
DELETE FROM _document_types
WHERE id = %s
RETURNING *;
"""

SELECT_DOCUMENT_TYPE_BY_ID = """
SELECT id, name, description
FROM _document_types
WHERE id = %s;
"""

SELECT_ALL_DOCUMENT_TYPES = """
SELECT *
FROM _document_types
"""

SELECT_DOCUMENT_TYPE_BY_NAME = """
SELECT id, name, description
FROM _document_types
WHERE name = %s;
""" 

