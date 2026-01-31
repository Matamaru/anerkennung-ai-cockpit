#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.requirements_sql              *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_REQUIREMENTS = """
CREATE TABLE IF NOT EXISTS _requirements (
    id VARCHAR(36) PRIMARY KEY,
    profession_id VARCHAR(36),
    country_id VARCHAR(36),
    state_id VARCHAR(36),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    optional BOOLEAN DEFAULT FALSE,
    translation_required BOOLEAN DEFAULT FALSE,
    fullfilled BOOLEAN DEFAULT FALSE,
    allow_multiple BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (profession_id) REFERENCES _professions(id),
    FOREIGN KEY (country_id) REFERENCES _countries(id),
    FOREIGN KEY (state_id) REFERENCES _states(id)
);
"""

DROP_TABLE_REQUIREMENTS = """
DROP TABLE IF EXISTS _requirements;
"""

INSERT_REQUIREMENT = """
INSERT INTO _requirements (id, profession_id, country_id, state_id, name, description, optional, translation_required, fullfilled, allow_multiple)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
RETURNING *
"""

UPDATE_REQUIREMENT = """
UPDATE _requirements
SET profession_id = %s, country_id = %s, state_id = %s, name = %s, description = %s, optional = %s, translation_required = %s, fullfilled = %s, allow_multiple = %s
WHERE id = %s
RETURNING *;
""" 

DELETE_REQUIREMENT = """
DELETE FROM _requirements
WHERE id = %s
RETURNING *;
""" 

SELECT_REQUIREMENT_BY_ID = """
SELECT id, profession_id, country_id, state_id, name, description, optional, translation_required, fullfilled, allow_multiple
FROM _requirements
WHERE id = %s;
""" 

SELECT_ALL_REQUIREMENTS = """
SELECT *
FROM _requirements
"""     

SELECT_REQUIREMENT_BY_NAME = """
SELECT id, profession_id, country_id, state_id, name, description, optional, translation_required, fullfilled, allow_multiple
FROM _requirements
WHERE name = %s;
"""

SELECT_REQUIREMENT_BY_NAME_AND_STATE = """
SELECT id, profession_id, country_id, state_id, name, description, optional, translation_required, fullfilled, allow_multiple
FROM _requirements
WHERE name = %s AND state_id = %s;
"""

SELECT_REQUIREMENTS_BY_PROFESSION_ID_COUNTRY_ID_STATE_ID = """
SELECT id, profession_id, country_id, state_id, name, description, optional, translation_required, fullfilled, allow_multiple
FROM _requirements
WHERE profession_id = %s AND country_id = %s AND state_id = %s;
"""
