#********************************************************************************
#	Application:	Anerkennung AI Cockpit	                    				*
#	Module:			backend.datamodule.models.role_sql 							*
#	Author:			Heiko Matamaru, IGS                     					*
#	Version:		0.0.1			                            				*
#********************************************************************************

#=== Imports
#=== defs and classes

CREATE_TABLE_ROLES = """
CREATE TABLE IF NOT EXISTS _roles (
    role_id VARCHAR(255) PRIMARY KEY NOT NULL,
    role_name VARCHAR(255) NOT NULL,
    description TEXT
)
"""

DROP_TABLE_ROLES = """
DROP TABLE IF EXISTS _roles;
"""

INSERT_ROLE = """
INSERT INTO _roles (
    role_id,
    role_name,
    description)
VALUES (
    %s,
    %s,
    %s)
RETURNING *
"""


UPDATE_ROLE = """
UPDATE _roles
SET role_name = %s, description = %s
WHERE role_id = %s
RETURNING *
"""

DELETE_ROLE = """
DELETE FROM _roles
WHERE role_id = %s
RETURNING *
"""

SELECT_ROLE_BY_ID = """
SELECT * FROM _roles
WHERE role_id = %s
"""

SELECT_ALL_ROLES = """
SELECT * FROM _roles
"""

SEARCH_ROLE_BY_NAME = """
SELECT * FROM _roles
WHERE role_name ILIKE %s
""" 