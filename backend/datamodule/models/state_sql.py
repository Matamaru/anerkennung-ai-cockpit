#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.state_sql                     *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

CREATE_TABLE_STATES = """
CREATE TABLE IF NOT EXISTS _states (
    id VARCHAR(36) PRIMARY KEY,
    country_id VARCHAR(36) NOT NULL,
    name VARCHAR(100) NOT NULL,
    abbreviation VARCHAR(10) NOT NULL,
    description TEXT
);
"""

DROP_TABLE_STATES = """
DROP TABLE IF EXISTS _states
"""

INSERT_STATE = """
INSERT INTO _states (id, country_id, name, abbreviation, description)
VALUES (%s, %s, %s, %s, %s)
RETURNING *
"""

UPDATE_STATE = """
UPDATE _states
SET country_id = %s, name = %s, abbreviation = %s, description = %s
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
SELECT id, country_id, name, abbreviation, description
FROM _states
WHERE id = %s
"""

SELECT_ALL_STATES = """
SELECT id, country_id, name, abbreviation, description
FROM _states
"""

SELECT_STATE_BY_NAME = """
SELECT id, country_id, name, abbreviation, description
FROM _states
WHERE name = %s
"""

SELECT_STATE_BY_ABBREVIATION = """
SELECT id, country_id, name, abbreviation, description
FROM _states
WHERE abbreviation = %s
"""

SELECT_STATES_BY_COUNTRY_ID = """
SELECT id, country_id, name, abbreviation, description
FROM _states
WHERE country_id = %s
"""

