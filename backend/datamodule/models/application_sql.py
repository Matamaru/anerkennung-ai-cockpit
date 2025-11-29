#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.application_sql                    *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_APPLICATION = """
CREATE TABLE IF NOT EXISTS _applications (
    id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    profession_id VARCHAR(36) NOT NULL,
    country_id VARCHAR(36) NOT NULL,
    state_id VARCHAR(36) NOT NULL,
    time_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES _users(id),
    FOREIGN KEY (profession_id) REFERENCES _profession(id),
    FOREIGN KEY (country_id) REFERENCES _country(id),
    FOREIGN KEY (state_id) REFERENCES _states(id)
);
"""

DROP_TABLE_APPLICATION = """
DROP TABLE IF EXISTS _applications;
"""

INSERT_APPLICATION = """
INSERT INTO _applications (id, user_id, profession_id, country_id, state_id)
VALUES (%s, %s, %s, %s, %s)
RETURNING *;
"""

UPDATE_APPLICATION = """
UPDATE _applications
SET user_id = %s, profession_id = %s, country_id = %s, state_id = %s
WHERE id = %s
RETURNING *;
"""

DELETE_APPLICATION = """
DELETE FROM _applications
WHERE id = %s
RETURNING *;
"""

SELECT_APPLICATION_BY_ID = """
SELECT id, user_id, profession_id, country_id, state_id, time_created
FROM _applications
WHERE id = %s;
"""

SELECT_ALL_APPLICATIONS = """
SELECT *
FROM _applications;
"""

SELECT_APPLICATIONS_BY_PROFESSION_ID = """
SELECT id, user_id, profession_id, country_id, state_id, time_created
FROM _applications
WHERE profession_id = %s;
"""

SELECT_APPLICATIONS_BY_COUNTRY_ID = """
SELECT id, user_id, profession_id, country_id, state_id, time_created
FROM _applications
WHERE country_id = %s;
"""

SELECT_APPLICATIONS_BY_STATE_ID = """
SELECT id, user_id, profession_id, country_id, state_id, time_created
FROM _applications
WHERE state_id = %s;
"""

SELECT_APPLICATIONS_BY_USER_ID = """
SELECT id, user_id, profession_id, country_id, state_id, time_created
FROM _applications
WHERE user_id = %s;
"""

