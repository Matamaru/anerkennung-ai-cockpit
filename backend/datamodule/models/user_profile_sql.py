#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.user_profile_sql             *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

CREATE_TABLE_USER_PROFILE = """
CREATE TABLE IF NOT EXISTS _user_profiles (
    user_id VARCHAR(255) PRIMARY KEY REFERENCES _users(user_id) ON DELETE CASCADE,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    birth_date VARCHAR(50),
    nationality VARCHAR(100),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    postal_code VARCHAR(50),
    city VARCHAR(100),
    country VARCHAR(100),
    phone VARCHAR(50),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

DROP_TABLE_USER_PROFILE = """
DROP TABLE IF EXISTS _user_profiles;
"""

SELECT_USER_PROFILE_BY_USER_ID = """
SELECT user_id, first_name, last_name, birth_date, nationality, address_line1, address_line2, postal_code, city, country, phone, updated_at
FROM _user_profiles
WHERE user_id = %s;
"""
