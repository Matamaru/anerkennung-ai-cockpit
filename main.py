#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:		    main	
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

#=== Imports
from frontend.webapp import create_app
from backend.datamodule import db
from backend.datamodule.models.user import User

#=== classes and defs

def main():
	# setup db
	db.connect()
	db.check_conn()
	db.create_tables()
	admin = User.create_admin()
	print(admin.to_json())
	is_user, user  = User.username_in_db(admin.username)
	if is_user:
		print(f"User {admin.username} already registered.")
	else:
		print(f"User {admin.username} is going to be registered ...")
#		admin.insert()
    
    
	# close db connection
	db.close_conn()

	# start app
	app = create_app()
	app.run(debug=True)


#=== main program

if __name__ == "__main__":
    main()