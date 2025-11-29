#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.role                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

from sre_parse import State
from uuid import uuid4
import psycopg2
from backend.datamodule.models.basemodel import *
from backend.datamodule.models.country import Country
from backend.datamodule.models.country_sql import SELECT_COUNTRY_BY_CODE
from backend.datamodule.models.profession_sql import SELECT_PROFESSION_BY_NAME
from backend.datamodule.models.state_sql import SELECT_STATE_BY_ABBREVIATION
from backend.datamodule.models.requirements_sql import *
from backend.datamodule import db

class Requirements(Model):
    def __init__(self, 
                 profession_id: str = None,
                 country_id: str = None, 
                 state_id: str = None, 
                 name: str = None, 
                 description: str = None, 
                 optional: bool = False, 
                 translation_required: bool = False, 
                 fullfilled: bool = False, 
                 id: str = None):
        if id:
            self.id = id
        else:
            self.id = str(uuid4())
        self.profession_id = profession_id
        self.country_id = country_id
        self.state_id = state_id
        self.name = name
        self.description = description
        self.optional = optional
        self.translation_required = translation_required
        self.fullfilled = fullfilled

    def __repr__(self):
        return f"<Requirement name={self.name} optional={self.optional} translation_required={self.translation_required} fullfilled={self.fullfilled}>"
    
    def insert(self) -> tuple:
        values = (self.id, self.profession_id, self.country_id, self.state_id, self.name, self.description, self.optional, self.translation_required, self.fullfilled)
        try:
            db.connect()
            # Execute insert
            db.cursor.execute(INSERT_REQUIREMENT, values)
            tuple_requirement = db.cursor.fetchone()

            if not tuple_requirement:
                raise InsertError("Failed to insert requirement into database.")
        
        except (Exception, psycopg2.DatabaseError) as error:
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_requirement

    def update(self, values: tuple) -> tuple:
        try:
            db.connect()
            # Execute update
            db.cursor.execute(UPDATE_REQUIREMENT, values)
            tuple_requirement = db.cursor.fetchone()

            if not tuple_requirement:
                raise UpdateError("Failed to update requirement in database.")
            
            return tuple_requirement

        except (Exception, psycopg2.DatabaseError) as error:
            raise UpdateError(error)

        finally:
            db.close_conn()

    def delete(self):
        try:
            db.connect()
            # Execute delete
            db.cursor.execute(DELETE_REQUIREMENT, (self.id,))
            tuple_requirement = db.cursor.fetchone()

            if not tuple_requirement:
                raise DeleteError("Failed to delete requirement from database.")
            
            return tuple_requirement

        except (Exception, psycopg2.DatabaseError) as error:
            raise DeleteError(error)

        finally:
            db.close_conn()

    @staticmethod
    def get_by_id(requirement_id: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_REQUIREMENT_BY_ID, (requirement_id,))
            tuple_requirement = db.cursor.fetchone()

            if not tuple_requirement:
                return None
            
            return tuple_requirement
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_name(name: str):
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_REQUIREMENT_BY_NAME, (name,))
            tuple_requirement = db.cursor.fetchone()

            if not tuple_requirement:
                return None
            
            return tuple_requirement
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_all():
        try:
            db.connect()
            # Execute select
            db.cursor.execute(SELECT_ALL_REQUIREMENTS)
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_optional(optional: bool):
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE optional = %s"
            db.cursor.execute(sql, (optional,))
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_fullfilled(fullfilled: bool):
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE fullfilled = %s"
            db.cursor.execute(sql, (fullfilled,))
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_translation_required(translation_required: bool):
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE translation_required = %s"
            db.cursor.execute(sql, (translation_required,))
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_country_id(country_id: str):
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE country_id = %s"
            db.cursor.execute(sql, (country_id,))
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_state_id(state_id: str) -> list:
        """
        Get list of requirements objects by state ID.
        
        :param state_id: State ID to filter requirements
        :return: List of requirements objects
        """
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE state_id = %s"
            db.cursor.execute(sql, (state_id,))
            requirements_tuple = db.cursor.fetchall()
            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_country_and_state_id(country_id: str, state_id: str) -> list:
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE country_id = %s AND state_id = %s"
            db.cursor.execute(sql, (country_id, state_id))
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_country_name(country_name: str) -> list:
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE country_id = (SELECT id FROM countries WHERE name = %s)"
            db.cursor.execute(sql, (country_name,))
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_state_name(state_name: str) -> list:
        try:
            db.connect()
            # Execute select
            sql = SELECT_ALL_REQUIREMENTS + " WHERE state_id = (SELECT id FROM states WHERE name = %s)"
            db.cursor.execute(sql, (state_name,))
            requirements_tuple = db.cursor.fetchall()

            if not requirements_tuple:
                return None
            
            return requirements_tuple
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()


    @staticmethod
    def from_tuple(t: tuple):
        return Requirements(
            id=t[0],
            profession_id=t[1],
            country_id=t[2],
            state_id=t[3],
            name=t[4],
            description=t[5],
            optional=t[6],
            translation_required=t[7],
            fullfilled=t[8]
        )
    
    @staticmethod
    def from_json(data: dict):
        return Requirements(
            id=data.get("id"),
            profession_id=data.get("profession_id"),
            country_id=data.get("country_id"),
            state_id=data.get("state_id"),
            name=data.get("name"),
            description=data.get("description"),
            optional=data.get("optional"),
            translation_required=data.get("translation_required"),
            fullfilled=data.get("fullfilled")
        )

    @staticmethod
    def create_default_requirements():
        # Default requirements data, e.g.: ID, degree, translation
        default_requirements = {
            "Nurse": {
                "DE-BY": [
                    {"name": "ID", "description": "Proof of identity (passport or ID card).", "optional": False, "translation_required_if_not_german": False, "fullfilled": False},
                    {"name": "CV", "description": "Tabular CV with date and signature.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "QualificationCertificate", "description": "Professional diploma / certificate.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "Transcript", "description": "List of subjects, hours and grades.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "ProfessionalExperience", "description": "Employment references or experience proofs.", "optional": True, "translation_required_if_not_german": False, "fullfilled": False},
                    {"name": "LanguageCertificate", "description": "German language certificate (B2 for nursing).", "optional": False, "translation_required_if_not_german": False, "fullfilled": False}
                ],
                "DE-NW": [
                    {"name": "ID", "description": "Proof of identity (passport or ID card).", "optional": False, "translation_required_if_not_german": False, "fullfilled": False},
                    {"name": "CV", "description": "Tabular CV with date and signature.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "QualificationCertificate", "description": "Professional diploma / certificate.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "Transcript", "description": "List of subjects, hours and grades.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "ProfessionalExperience", "description": "Employment references or experience proofs.", "optional": True, "translation_required_if_not_german": False, "fullfilled": False},
                    {"name": "LanguageCertificate", "description": "German language certificate (B2 for nursing).", "optional": False, "translation_required_if_not_german": False, "fullfilled": False}
                ],
                "DE-BE": [
                    {"name": "ID", "description": "Proof of identity (passport or ID card).", "optional": False, "translation_required_if_not_german": False, "fullfilled": False},
                    {"name": "CV", "description": "Tabular CV with date and signature.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "QualificationCertificate", "description": "Professional diploma / certificate.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "Transcript", "description": "List of subjects, hours and grades.", "optional": False, "translation_required_if_not_german": True, "fullfilled": False},
                    {"name": "ProfessionalExperience", "description": "Employment references or experience proofs.", "optional": True, "translation_required_if_not_german": False, "fullfilled": False},
                    {"name": "LanguageCertificate", "description": "German language certificate (B2 for nursing).", "optional": False, "translation_required_if_not_german": False, "fullfilled": False},
                    {"name": "ProofOfBerlinResponsibility", "description": "Proof that Berlin is the responsible state (residence, employer, or job offer).", "optional": False, "translation_required_if_not_german": False, "fullfilled": False}
                ]
            }        
            }
    
        try:
            db.connect()
    
            # Loop through professions (e.g., Nurse)
            for profession_name, states in default_requirements.items():
                #print(f"Processing profession: {profession_name}")
                # Fetch the profession_id (e.g., "Nurse")
                db.cursor.execute(SELECT_PROFESSION_BY_NAME, (profession_name,))
                profession_tuple = db.cursor.fetchone()
                #print(f"profession_tuple for {profession_name}: {profession_tuple}")
                profession_id = profession_tuple[0] if profession_tuple else None
    
                if not profession_id:
                    print(f"Profession '{profession_name}' not found.")
                    continue
                
                # Loop through states (e.g., "DE-BY", "DE-NW")
                for state_code, requirements in states.items():
                    #print(f"Processing default requirements for profession '{profession_name}' in state '{state_code}'")
                    # Get country_id and state_id
                    country_code, state_abbr = state_code.split("-")
                    #print(f"country_code: {country_code}")
                    #print(f"state_abbr: {state_abbr}")

                    # Fetch country_id
                    db.cursor.execute(SELECT_COUNTRY_BY_CODE, (country_code,))
                    country_tuple = db.cursor.fetchone()
                    #print(f"country_tuple for code {country_code}: {country_tuple}")
                    country_id = country_tuple[0] if country_tuple else None
                    
                    # Fetch state_id, use state code as abbreviation
                    db.cursor.execute(SELECT_STATE_BY_ABBREVIATION, (state_code,))
                    state_tuple = db.cursor.fetchone()
                    state_id = state_tuple[0] if state_tuple else None
    
                    if not country_id or not state_id:
                        print(f"Country or state not found for code: {state_code}")
                        continue
                    
                    # Insert the requirements for this state and profession
                    for req in requirements:
                        values = (
                            str(uuid4()),  # Generate new UUID
                            profession_id,  # Profession ID (e.g., Nurse)
                            country_id,  # Country ID
                            state_id,  # State ID
                            req["name"],  # Requirement name (ID, CV, etc.)
                            req["description"],  # Description
                            req["optional"],  # Optional
                            req["translation_required_if_not_german"],  # Translation requirement
                            req["fullfilled"]  # Fulfilled status
                        )
    
                        # Check if requirement already exists
                        query = """
                         SELECT *
                         FROM _requirements
                         WHERE profession_id = %s AND country_id = %s AND state_id = %s AND name = %s
                        """
                        db.cursor.execute(SELECT_REQUIREMENTS_BY_PROFESSION_ID_COUNTRY_ID_STATE_ID, (profession_id, country_id, state_id))
                        existing_req = db.cursor.fetchone()
                        if existing_req:
                            if existing_req[4] == req["name"]:
                                print(f"Requirement {req['name']} for {state_code} already exists. Skipping.")
                                continue
                            else:
                                print(f"Requirement {req['name']} for {state_code} does not exist. Inserting.")
                        
                        # Insert the requirement into the database
                        db.cursor.execute(INSERT_REQUIREMENT, values)
                        print(f"Inserted default requirement '{req['name']}' for {state_code}.")
    
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating default requirements: {error}")
        finally:
            db.close_conn()
    