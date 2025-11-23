#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.country                       *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.country_sql import *
from backend.datamodule import db   

#=== Country Model
class Country(Model):
    def __init__(self, name: str = None, abbreviation: str = None, description: str = None, id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.name = name
        self.abbreviation = abbreviation
        self.description = description

    def __repr__(self):
        return f"<Country name={self.name} abbreviation={self.abbreviation}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.name, self.abbreviation, self.description)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_COUNTRY, values)
            tuple_country = db.cursor.fetchone()

            if not tuple_country:
                raise InsertError("Failed to insert country into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_country
        
    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_COUNTRY, values)
            tuple_country = db.cursor.fetchone()

            if not tuple_country:
                raise UpdateError("Failed to update country in database.")
            
            return tuple_country

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)
        
        finally:
            db.close_conn()

    def delete(self) -> tuple:
        values = (self.id,)
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_COUNTRY, values)
            tuple_country = db.cursor.fetchone()

            if not tuple_country:
                raise DeleteError("Failed to delete country from database.")
            
            return tuple_country

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def from_tuple(tuple_country: tuple):
        if tuple_country:
            return Country(
                id=tuple_country[0],
                name=tuple_country[1],
                abbreviation=tuple_country[2],
                description=tuple_country[3]
            )
        return None
    
    @staticmethod
    def from_json(json_country: dict):
        if json_country:
            return Country(
                id=json_country.get("id"),
                name=json_country.get("name"),
                abbreviation=json_country.get("abbreviation"),
                description=json_country.get("description")
            )
        return None
    
    @staticmethod
    def get_by_id(id: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_COUNTRY_BY_ID, (id,))
            tuple_country = db.cursor.fetchone()

            if not tuple_country:
                raise RecordNotFoundError("Country not found in database.")
            
            return tuple_country

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn()


    @staticmethod
    def get_by_name(name: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_COUNTRY_BY_NAME, (name,))
            tuple_country = db.cursor.fetchone()

            if not tuple_country:
                raise RecordNotFoundError("Country not found in database.")
            
            return tuple_country

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)
        
        finally:
            db.close_conn()

    @staticmethod
    def get_all() -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_ALL_COUNTRIES)
            tuples_countries = db.cursor.fetchall()

            return tuples_countries

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn() 

    @staticmethod
    def get_by_code(code: str) -> tuple:
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_COUNTRY_BY_CODE, (code,))
            tuple_country = db.cursor.fetchone()

            if not tuple_country:
                raise RecordNotFoundError("Country not found in database.")
            
            return tuple_country

        except (Exception, psycopg2.DatabaseError) as error:
            raise RecordNotFoundError(error)

        finally:
            db.close_conn()

    @staticmethod
    def create_default_countries() -> tuple:
        # country code ISO 3166-1 alpha-2
        default_countries = [
            ("Germany", "DE", "Germany")
            # Add more default countries as needed        
            ]
        try:
            db.connect()
            # Execute insert default countries
            for country in default_countries:
                # check if country already exists
                db.cursor.execute(SELECT_COUNTRY_BY_CODE, (country[1],))
                tuple_country = db.cursor.fetchone()
                if not tuple_country:
                    values = (str(uuid4()), country[0], country[1], country[2])
                    db.cursor.execute(INSERT_COUNTRY, values)
                    print(f"Inserted default country '{country[0]}'.")
                else:
                    print(f"Country '{country[0]}' already exists.")
            db.conn.commit()
            return Country.get_all()
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)
        finally:
            db.close_conn()