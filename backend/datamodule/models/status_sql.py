#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.status_sql                    *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_STATUS = """
CREATE TABLE IF NOT EXISTS _statuses (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT
);
"""

DROP_TABLE_STATUS = """
DROP TABLE IF EXISTS _statuses;
""" 

INSERT_STATUS = """
INSERT INTO _statuses (id, name, description)
VALUES (%s, %s, %s)
RETURNING *
""" 

UPDATE_STATUS = """
UPDATE _statuses
SET name = %s, description = %s
WHERE id = %s
RETURNING *;
""" 

DELETE_STATUS = """
DELETE FROM _statuses
WHERE id = %s
RETURNING *;
""" 

SELECT_STATUS_BY_ID = """
SELECT id, name, description
FROM _statuses
WHERE id = %s;
""" 

SELECT_ALL_STATUS = """
SELECT *
FROM _statuses
""" 

SELECT_BY_NAME = """
SELECT id, name, description
FROM _statuses
WHERE name = %s;
"""

