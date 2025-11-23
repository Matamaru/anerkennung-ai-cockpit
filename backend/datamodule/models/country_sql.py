#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.country_sql                   *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_COUNTRY = """
CREATE TABLE IF NOT EXISTS _countries (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    code VARCHAR(10) NOT NULL,
    description TEXT
);
""" 

DROP_TABLE_COUNTRY = """
DROP TABLE IF EXISTS _countries;
"""

INSERT_COUNTRY = """
INSERT INTO _countries (id, name, code, description)
VALUES (%s, %s, %s, %s)
RETURNING *;
""" 

UPDATE_COUNTRY = """
UPDATE _countries
SET name = %s, code = %s, description = %s
WHERE id = %s
RETURNING *;
""" 

DELETE_COUNTRY = """
DELETE FROM _countries
WHERE id = %s   
RETURNING *;
"""     

SELECT_COUNTRY_BY_ID = """
SELECT id, name, code, description
FROM _countries     
WHERE id = %s
""";    

SELECT_ALL_COUNTRIES = """             
SELECT *
FROM _countries
""" 

SELECT_COUNTRY_BY_NAME = """
SELECT id, name, code, description
FROM _countries     
WHERE name = %s
""";    

SELECT_COUNTRY_BY_CODE = """
SELECT id, name, code, description
FROM _countries     
WHERE code = %s
""";

