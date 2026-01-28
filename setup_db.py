#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:		    setup_db	
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

from backend.datamodule import Base, engine
from backend.datamodule.models.profession import Profession
from backend.datamodule.models.requirements import Requirements
from backend.datamodule.models.country import Country
from backend.datamodule.models.document_type import DocumentType
from backend.datamodule.models.file_type import FileType
from backend.datamodule.models.state import State
from backend.datamodule.models.status import Status
from backend.datamodule.models.role import Role
from backend.datamodule.models.user import User

try:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    #=== roles and admin user
    Role.create_default_roles()

    admin = User.create_admin()
    is_user, _ = User.username_in_db(admin.username)
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
    DocumentType.create_default_document_types()
    Status.create_default_statuses()
    FileType.create_default_file_types()

    #=== requirements related dependencies
    Country.create_default_countries()
    State.create_default_states()
    Profession.create_default_professions()
    Requirements.create_default_requirements()

except Exception as error:
    print(f"Error during database setup: {error}")
