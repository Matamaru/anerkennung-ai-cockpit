#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:		    main	
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

#=== Imports
from frontend.webapp import create_app
from backend.datamodule.config import config_db
from backend.datamodule.datamodule import DataBase

#=== classes and defs

def main():
	
    # get db_params from ENV
	db_params = config_db()

    # Connect to database
	db = DataBase(db_params)
	db.connect()
	db.check_conn()
	db.close_conn()

	# start app
	app = create_app()
	app.run(debug=True)


#=== main program

if __name__ == "__main__":
    main()