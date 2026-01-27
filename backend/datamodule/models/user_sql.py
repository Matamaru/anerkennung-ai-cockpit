#********************************************************************************
#	Application:	Anerkennung AI Cockpit	                    				*
#	Module:			backend.datamodule.models.user_sql 							*
#	Author:			Heiko Matamaru, IGS                     					*
#	Version:		0.0.1			                            				*
#********************************************************************************

#=== Imports

#=== defs and classes

CREATE_TABLE_USERS = """
CREATE TABLE IF NOT EXISTS _users (
	user_id VARCHAR(255) PRIMARY KEY NOT NULL,
    role_id VARCHAR(255) NOT NULL,
	username VARCHAR(255) NOT NULL,
	password VARCHAR(255) NOT NULL,
	email VARCHAR(255) UNIQUE NOT NULL,
    b_admin BOOLEAN DEFAULT FALSE,
	salt VARCHAR(255) NOT NULL,
	pepper VARCHAR(255) NOT NULL,
	FOREIGN KEY (role_id) REFERENCES _roles(role_id)
	)
"""

DROP_TABLE_USERS = """
DROP TABLE IF EXISTS _users;
"""

INSERT_USER = """
INSERT INTO _users (
	user_id,
	role_id,
	username,
	password,
	email,
	b_admin,
	salt,
	pepper
	)
VALUES (
	%s,
	%s,
	%s,
	%s,
	%s,
    %s,
	%s,
	%s)
	RETURNING *
"""

UPDATE_USER = """
UPDATE _users 
SET role_id = %s, username = %s, password = %s, email = %s, b_admin = %s, salt = %s, pepper = %s
WHERE user_id = %s
RETURNING *
"""

DELETE_USER = """
DELETE FROM _users
WHERE user_id = %s
RETURNING *
"""

DELETE_USER_BY_USERNAME = """
DELETE FROM _users
WHERE username = %s
RETURNING *
"""

SELECT_USER_BY_ID = """
SELECT * FROM _users
WHERE user_id = %s
"""

SELECT_USER_BY_USERNAME = """
SELECT * FROM _users
WHERE username = %s
"""

SELECT_USER_BY_EMAIL = """
SELECT * FROM _users
WHERE email = %s
"""

SELECT_ALL_USERS = """
SELECT * FROM _users
"""

COUNT_USERS = """
SELECT COUNT(*) FROM _users
"""

SELECT_USERS_BY_ROLE_NAME = """
SELECT u.* FROM _users u
JOIN _roles r ON u.role_id = r.role_id
WHERE r.role_name LIKE %s
"""
