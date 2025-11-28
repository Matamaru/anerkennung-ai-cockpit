#****************************************************************************
#   Module:             backend.datamodule.config (Anerkennung AI Cockpit)  *
#   Author:             Heiko Matamaru, IGS                                 *
#   Version:            0.0.1                                               *
#****************************************************************************

#=== Imports

import os
from dotenv import load_dotenv
from urllib.parse import urlparse

# load .env file
load_dotenv()

#=== defs and classes

def config_db():
    # db dict
    db = {}

    # Get the DATABASE_URL from the environment variable (set by Heroku)
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # If DATABASE_URL is not set, raise an error
    if DATABASE_URL is None:
        raise ValueError("DATABASE_URL environment variable not set")
    
    # Parse the DATABASE_URL
    result = urlparse(DATABASE_URL)
    
    # Extract connection details from the parsed URL
    db['host'] = result.hostname
    db['port'] = result.port
    db['dbname'] = result.path[1:]  # Remove leading '/' from path
    db['user'] = result.username
    db['password'] = result.password

    return db

#=== main

if __name__ == "__main__":
    db_config = config_db()
    print(db_config)
