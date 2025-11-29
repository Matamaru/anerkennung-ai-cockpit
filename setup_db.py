#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:		    setup_db	
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

#=== Imports
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.requirements import Requirements
from backend.datamodule.models.country import Country
from backend.datamodule.models.document_type import DocumentType
from backend.datamodule.models.file_type import FileType
from backend.datamodule.models.state import State
from backend.datamodule.models.status import Status
from backend.datamodule import db
from backend.datamodule.models.role import Role
from backend.datamodule.models.user import User


# setup db
try:
	db.connect()
	db.check_conn()

	# in case of testing, drop all tables first, else comment out
	#db.drop_all_tables()
     
	# create tables if not existing
	db.create_all_tables()

	#=== roles and admin user
	# create default roles if not existing
	Role.create_default_roles()

 	# create admin user if not existing
	admin = User.create_admin()
	
	#print(admin.to_json())
	is_user, user  = User.username_in_db(admin.username)
	if is_user:
		print(f"User {admin.username} already registered.")
	else:
		print(f"User {admin.username} is going to be registered ...")
		admin_tuple = admin.insert()
		if admin:
			print(f"User {admin_tuple[1]} registered successfully.")
		else:
			print(f"User {admin_tuple[1]} could not be registered.")

	#=== default document dependencies
	# default document types
	DocumentType.create_default_document_types()

	# default statuses
	Status.create_default_statuses()

	# default file types
	FileType.create_default_file_types()

	#=== requirements related dependencies
	# default countries
	Country.create_default_countries()

	# default states
	State.create_default_states()

	# default requirements
	Requirements.create_default_requirements()

	# default professions
	Profession.create_default_professions()

except Exception as error:
	print(f"Error during database setup: {error}")
finally:
	db.close_conn()