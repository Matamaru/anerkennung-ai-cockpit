#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.role                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

CREATE_TABLE_STATES = """
CREATE TABLE IF NOT EXISTS _states (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL,
    description TEXT
)
RETURNING *;
"""

DROP_TABLE_STATES = """
DROP TABLE IF EXISTS state
RETURNING *;
"""

INSERT_STATE = """
INSERT INTO _states (id, name, abbreviation, description)
VALUES (%s, %s, %s, %s)
RETURNING *;
"""

UPDATE_STATE = """
UPDATE _states
SET name = %s, abbreviation = %s, description = %s
WHERE id = %s
RETURNING *;
"""

DELETE_STATE = """
DELETE FROM _states
WHERE id = %s
RETURNING *;
"""

DELETE_STATE_BY_NAME = """
DELETE FROM _states
WHERE name = %s
RETURNING *;
"""

SELECT_STATE_BY_ID = """
SELECT id, name, abbreviation, description
FROM _states
WHERE id = %s
RETURNING *;
"""

SELECT_ALL_STATES = """
SELECT id, name, abbreviation, description
FROM _states
RETURNING *;
"""

SELECT_STATE_BY_NAME = """
SELECT id, name, abbreviation, description
FROM _states
WHERE name = %s
RETURNING *;
"""

SELECT_STATE_BY_ABBREVIATION = """
SELECT id, name, abbreviation, description
FROM _states
WHERE abbreviation = %s
RETURNING *;
"""