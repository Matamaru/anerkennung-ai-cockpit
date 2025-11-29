#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:		    main	
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

#=== Imports
from frontend.webapp import create_app

#=== Create Flask App
app = create_app()	

if __name__ == "__main__":
	app.run(debug=True)
