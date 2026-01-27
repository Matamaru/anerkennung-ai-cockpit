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

    # Prefer DATABASE_URL (Heroku-style)
    DATABASE_URL = os.getenv("DATABASE_URL")

    if DATABASE_URL:
        # Parse the DATABASE_URL
        result = urlparse(DATABASE_URL)
        # Extract connection details from the parsed URL
        db['host'] = result.hostname
        db['port'] = result.port
        db['dbname'] = result.path[1:]  # Remove leading '/' from path
        db['user'] = result.username
        db['password'] = result.password
        return db

    # Local fallback
    db['host'] = os.getenv("DB_HOST", "localhost")
    db['port'] = int(os.getenv("DB_PORT", "5432"))
    db['dbname'] = os.getenv("DB_NAME")
    db['user'] = os.getenv("DB_USER")
    db['password'] = os.getenv("DB_PASSWORD")

    missing = [k for k, v in db.items() if v in (None, "")]
    if missing:
        raise ValueError(f"Missing DB config values: {', '.join(missing)}")

    return db

#=== main

if __name__ == "__main__":
    db_config = config_db()
    print(db_config)
