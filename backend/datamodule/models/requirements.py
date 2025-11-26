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
from backend.datamodule.models.state_sql import SELECT_STATE_BY_ABBREVIATION
from backend.datamodule.models.requirements_sql import *
from backend.datamodule import db

class Requirements(Model):
    def __init__(self, 
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
        values = (self.id, self.country_id, self.state_id, self.name, self.description, self.optional, self.translation_required, self.fullfilled)
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
            
            return Requirements.from_tuple(tuple_requirement)
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
            
            return Requirements.from_tuple(tuple_requirement)
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
            country_id=t[1],
            state_id=t[2],
            name=t[3],
            description=t[4],
            optional=t[5],
            translation_required=t[6],
            fullfilled=t[7]
        )
    
    @staticmethod
    def from_json(data: dict):
        return Requirements(
            id=data.get("id"),
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
        # default requirements data, e.g.: ID, degree, translation
        default_requirements = {

            "DE-BY": [
                {
                    "name": "ID",
                    "description": "Proof of identity (passport or ID card). Translation usually not required unless script is non-Latin.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "CV",
                    "description": "Tabular CV with date and signature.",
                    "optional": False,
                    "translation_required_if_not_german": True,
                    "fullfilled": False
                },
                {
                    "name": "QualificationCertificate",
                    "description": "Professional diploma / certificate. Certified German translation required if not issued in German.",
                    "optional": False,
                    "translation_required_if_not_german": True,
                    "fullfilled": False
                },
                {
                    "name": "Transcript",
                    "description": "List of subjects, hours and grades (training content). Certified German translation required if not issued in German.",
                    "optional": False,
                    "translation_required_if_not_german": True,
                    "fullfilled": False
                },
                {
                    "name": "ProfessionalExperience",
                    "description": "Employment references or experience proofs. Often need German translations; exact rule depends on authority.",
                    "optional": True,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "BirthCertificate",
                    "description": "Birth certificate (and name-change certificate if relevant). Translation may be required if not in German; check authority.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                               "fullfilled": False
                },
                {
                    "name": "PoliceClearance",
                    "description": "Police record extract / certificate of good conduct. Translation may be required if not in German; check authority.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "MedicalCertificate",
                    "description": "Medical fitness certificate (if required). Translation may be required if not in German; check authority.",
                    "optional": True,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "LanguageCertificate",
                    "description": "German language certificate (usually B2 for nursing). Normally issued directly in German; no translation necessary.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                }
            ],

            "DE-NW": [
                {
                    "name": "ID",
                    "description": "Proof of identity (passport or ID card). Translation usually not required unless script is non-Latin.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "CV",
                    "description": "Tabular CV with date and signature (usually created directly in German, no translation of a foreign CV).",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "QualificationCertificate",
                    "description": "Professional diploma / certificate. Certified German translation required if not issued in German.",
                    "optional": False,
                    "translation_required_if_not_german": True,
                    "fullfilled": False
                },
                {
                    "name": "Transcript",
                    "description": "List of subjects, hours and grades (training content). Certified German translation required if not issued in German.",
                    "optional": False,
                    "translation_required_if_not_german": True,
                    "fullfilled": False
                },
                {
                    "name": "ProfessionalExperience",
                    "description": "Employment references or experience proofs. Often need German translations; exact rule depends on authority.",
                    "optional": True,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "BirthCertificate",
                    "description": "Birth certificate (and name-change certificate if relevant). Translation may be required if not in German; check authority.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "PoliceClearance",
                    "description": "Police record extract / certificate of good conduct. Translation may be required if not in German; check authority.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "MedicalCertificate",
                    "description": "Medical fitness certificate (if required). Translation may be required if not in German; check authority.",
                    "optional": True,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "LanguageCertificate",
                    "description": "German language certificate (usually B2 for nursing). Normally issued directly in German; no translation necessary.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                }
            ],

            "DE-BE": [
                {
                    "name": "ID",
                    "description": "Proof of identity (passport or ID card). Translation usually not required unless script is non-Latin.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "CV",
                    "description": "Tabular CV with date and signature (usually created directly in German, no translation of a foreign CV).",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "QualificationCertificate",
                    "description": "Professional diploma / certificate. Certified German translation required if not issued in German.",
                    "optional": False,
                    "translation_required_if_not_german": True,
                    "fullfilled": False
                },
                {
                    "name": "Transcript",
                    "description": "List of subjects, hours and grades (training content). Certified German translation required if not issued in German.",
                    "optional": False,
                    "translation_required_if_not_german": True,
                    "fullfilled": False
                },
                {
                    "name": "ProfessionalExperience",
                    "description": "Employment references or experience proofs. Often need German translations; exact rule depends on authority.",
                    "optional": True,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "BirthCertificate",
                    "description": "Birth certificate (and name-change certificate if relevant). Translation may be required if not in German; check authority.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "PoliceClearance",
                    "description": "Police record extract / certificate of good conduct. Translation may be required if not in German; check authority.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "MedicalCertificate",
                    "description": "Medical fitness certificate (if required). Translation may be required if not in German; check authority.",
                    "optional": True,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },
                {
                    "name": "LanguageCertificate",
                    "description": "German language certificate (usually B2 for nursing). Normally issued directly in German; no translation necessary.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                },

                {
                    "name": "ProofOfBerlinResponsibility",
                    "description": "Proof that Berlin is the responsible state (residence, employer, or job offer in Berlin). Usually in German; translation rarely required.",
                    "optional": False,
                    "translation_required_if_not_german": False,
                    "fullfilled": False
                }
            ]
        }

        try:
            db.connect()
            # Execute insert default requirements
            for state_code, requirements in default_requirements.items():
                country_code, state_abbr = state_code.split("-")
                #print(f"country_code: {country_code}, state_abbr: {state_abbr}")
                # Get country_id and state_id from Country and State models
                db.cursor.execute(SELECT_COUNTRY_BY_CODE, (country_code,))
                country_tuple = db.cursor.fetchone()
               # if not country_tuple:
               #     print(f"Country not found for code: {country_code}")
               #     continue
                country_id = country_tuple[0] if country_tuple else None
                # Search for state code in states table instead if state abbbreviation, eg. "DE-BY" for Bavaria!
                db.cursor.execute(SELECT_STATE_BY_ABBREVIATION, (state_code,))
                state_tuple = db.cursor.fetchone()
                # if not state_tuple:
                #     print(f"State not found for abbreviation: {state_abbr}")
                #     continue
                state_id = state_tuple[0] if state_tuple else None
                if not country_id or not state_id:
                    print(f"Country or State not found for code: {state_code}")
                    continue
                for req in requirements:
                    values = (
                        str(uuid4()), 
                        country_id,
                        state_id,
                        req["name"],
                        req["description"],
                        req["optional"],
                        req["translation_required_if_not_german"],
                        req["fullfilled"]
                    )
                    # Check if requirement already exists
                    db.cursor.execute(SELECT_REQUIRMENT_BY_NAME_AND_STATE, (req["name"], state_id))
                    existing_req = db.cursor.fetchone()            
                    if existing_req:
                        print(f"Requirement {req['name']} for {state_code} already exists. Skipping.")
                        continue
                    # Insert requirement
                    db.cursor.execute(INSERT_REQUIREMENT, values)
                    print(f"Inserted default requirement '{req['name']}' for {state_code}.")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error creating default requirements: {error}")
        finally:
            db.close_conn()