#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:		    main	
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

#=== Imports
from frontend.webapp import create_app
from backend.datamodule import db

#=== classes and defs

def main():
	# setup db
	db.connect()
	db.check_conn()
	db.create_tables()

	# close db connection
	db.close_conn()

	# start app
	app = create_app()
	app.run(debug=True)


#=== main program

if __name__ == "__main__":
    main()