#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.profession_sql                *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_PROFESSION = """
CREATE TABLE IF NOT EXISTS _professions (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);
"""

DROP_TABLE_PROFESSION = """
DROP TABLE IF EXISTS _professions;
"""

INSERT_PROFESSION = """
INSERT INTO _professions (id, name, description)
VALUES (%s, %s, %s)
RETURNING *;
"""

UPDATE_PROFESSION = """
UPDATE _professions
SET name = %s, description = %s
WHERE id = %s
RETURNING *;
"""

DELETE_PROFESSION = """
DELETE FROM _professions
WHERE id = %s
RETURNING *;
""" 

SELECT_PROFESSION_BY_ID = """
SELECT id, name, description
FROM _professions
WHERE id = %s;
"""

SELECT_ALL_PROFESSIONS = """
SELECT *
FROM _professions;
"""

SELECT_PROFESSION_BY_NAME = """
SELECT id, name, description
FROM _professions
WHERE name = %s;
"""

