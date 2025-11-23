#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.file_type_sql                 *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_FILE_TYPE = """
CREATE TABLE IF NOT EXISTS _file_types (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);
"""

DROP_TABLE_FILE_TYPE = """
DROP TABLE IF EXISTS _file_types;
""" 

INSERT_FILE_TYPE = """
INSERT INTO _file_types (id, name, description)
VALUES (%s, %s, %s)
RETURNING *
"""

UPDATE_FILE_TYPE = """
UPDATE _file_types
SET name = %s, description = %s
WHERE id = %s
RETURNING *;
""" 

DELETE_FILE_TYPE = """
DELETE FROM _file_types
WHERE id = %s
RETURNING *;
""" 

SELECT_FILE_TYPE_BY_ID = """
SELECT id, name, description
FROM _file_types
WHERE id = %s;
"""

SELECT_ALL_FILE_TYPES = """
SELECT *
FROM _file_types
""" 

SELECT_FILE_TYPE_BY_NAME = """
SELECT id, name, description
FROM _file_types
WHERE name = %s;
"""

