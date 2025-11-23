#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.file_sql                      *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_FILE = """
CREATE TABLE IF NOT EXISTS _files (
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    filetype_id VARCHAR(36) REFERENCES _file_types(id),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP     
);
"""

DROP_TABLE_FILE = """
DROP TABLE IF EXISTS _files;
""" 

INSERT_FILE = """
INSERT INTO _files (id, filename, filepath, filetype_id)
VALUES (%s, %s, %s, %s)
RETURNING *
"""

UPDATE_FILE = """
UPDATE _files
SET filename = %s, filepath = %s, filetype_id = %s
WHERE id = %s
RETURNING *;
"""

DELETE_FILE = """
DELETE FROM _files
WHERE id = %s
RETURNING *;
"""

SELECT_FILE_BY_ID = """
SELECT id, filename, filepath, filetype_id, uploaded_at
FROM _files
WHERE id = %s;
""" 

SELECT_ALL_FILES = """
SELECT *
FROM _files
"""

SELECT_FILE_BY_NAME = """
SELECT id, filename, filepath, filetype_id, uploaded_at
FROM _files
WHERE filename = %s;
"""

SELECT_FILE_BY_FILETYPE = """
SELECT id, filename, filepath, filetype_id, uploaded_at
FROM _files
WHERE filetype_id = %s;
"""

SELECT_ALL_FILES_BY_FILETYPE_ID = """
SELECT id, filename, filepath, filetype_id, uploaded_at
FROM _files
WHERE filetype_id = %s;
"""

SELECT_ALL_FILES_BY_FILETYPE_NAME = """
SELECT f.id, f.filename, f.filepath, f.filetype_id, f.uploaded_at
FROM _files f
JOIN _file_types ft ON f.filetype_id = ft.id
WHERE ft.name = %s;
"""



