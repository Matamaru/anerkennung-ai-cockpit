#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.requirements                  *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Country as CountryORM, Profession as ProfessionORM, Requirement as RequirementORM, State as StateORM
from backend.datamodule.sa import session_scope


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
                 allow_multiple: bool = True,
                 id: str = None):
        self.id = id or str(uuid4())
        self.profession_id = profession_id
        self.country_id = country_id
        self.state_id = state_id
        self.name = name
        self.description = description
        self.optional = optional
        self.translation_required = translation_required
        self.fullfilled = fullfilled
        self.allow_multiple = allow_multiple

    def __repr__(self):
        return f"<Requirement name={self.name} optional={self.optional} translation_required={self.translation_required} fullfilled={self.fullfilled}>"
    
    def insert(self) -> tuple:
        try:
            with session_scope() as session:
                orm_req = RequirementORM(
                    id=self.id,
                    profession_id=self.profession_id,
                    country_id=self.country_id,
                    state_id=self.state_id,
                    name=self.name,
                    description=self.description,
                    optional=self.optional,
                    translation_required=self.translation_required,
                    fullfilled=self.fullfilled,
                    allow_multiple=self.allow_multiple,
                )
                session.add(orm_req)
                session.flush()
                return Requirements._as_tuple(orm_req)
        except Exception as error:
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        try:
            with session_scope() as session:
                orm_req = session.query(RequirementORM).filter_by(id=values[9]).first()
                if not orm_req:
                    raise UpdateError("Failed to update requirement in database.")
                orm_req.profession_id = values[0]
                orm_req.country_id = values[1]
                orm_req.state_id = values[2]
                orm_req.name = values[3]
                orm_req.description = values[4]
                orm_req.optional = values[5]
                orm_req.translation_required = values[6]
                orm_req.fullfilled = values[7]
                orm_req.allow_multiple = values[8]
                session.flush()
                return Requirements._as_tuple(orm_req)
        except Exception as error:
            raise UpdateError(error)

    def delete(self):
        try:
            with session_scope() as session:
                orm_req = session.query(RequirementORM).filter_by(id=self.id).first()
                if not orm_req:
                    raise DeleteError("Failed to delete requirement from database.")
                session.delete(orm_req)
                return Requirements._as_tuple(orm_req)
        except Exception as error:
            raise DeleteError(error)

    @staticmethod
    def get_by_id(requirement_id: str):
        with session_scope() as session:
            orm_req = session.query(RequirementORM).filter_by(id=requirement_id).first()
            return Requirements._as_tuple(orm_req) if orm_req else None

    @staticmethod
    def get_by_name(name: str):
        with session_scope() as session:
            orm_req = session.query(RequirementORM).filter_by(name=name).first()
            return Requirements._as_tuple(orm_req) if orm_req else None

    @staticmethod
    def get_all():
        with session_scope() as session:
            reqs = session.query(RequirementORM).all()
            return [Requirements._as_tuple(r) for r in reqs]

    @staticmethod
    def get_by_optional(optional: bool):
        with session_scope() as session:
            reqs = session.query(RequirementORM).filter_by(optional=optional).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

    @staticmethod
    def get_by_fullfilled(fullfilled: bool):
        with session_scope() as session:
            reqs = session.query(RequirementORM).filter_by(fullfilled=fullfilled).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

    @staticmethod
    def get_by_translation_required(translation_required: bool):
        with session_scope() as session:
            reqs = session.query(RequirementORM).filter_by(translation_required=translation_required).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

    @staticmethod
    def get_by_country_id(country_id: str):
        with session_scope() as session:
            reqs = session.query(RequirementORM).filter_by(country_id=country_id).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

    @staticmethod
    def get_by_state_id(state_id: str) -> list:
        with session_scope() as session:
            reqs = session.query(RequirementORM).filter_by(state_id=state_id).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

    @staticmethod
    def get_by_country_and_state_id(country_id: str, state_id: str) -> list:
        with session_scope() as session:
            reqs = session.query(RequirementORM).filter_by(country_id=country_id, state_id=state_id).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

    @staticmethod
    def get_by_country_name(country_name: str) -> list:
        with session_scope() as session:
            country = session.query(CountryORM).filter_by(name=country_name).first()
            if not country:
                return None
            reqs = session.query(RequirementORM).filter_by(country_id=country.id).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

    @staticmethod
    def get_by_state_name(state_name: str) -> list:
        with session_scope() as session:
            state = session.query(StateORM).filter_by(name=state_name).first()
            if not state:
                return None
            reqs = session.query(RequirementORM).filter_by(state_id=state.id).all()
            return [Requirements._as_tuple(r) for r in reqs] if reqs else None

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
            fullfilled=t[8],
            allow_multiple=t[9] if len(t) > 9 else None
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
            fullfilled=data.get("fullfilled"),
            allow_multiple=data.get("allow_multiple"),
        )

    @staticmethod
    def create_default_requirements():
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
            with session_scope() as session:
                for profession_name, states in default_requirements.items():
                    profession = session.query(ProfessionORM).filter_by(name=profession_name).first()
                    if not profession:
                        print(f"Profession '{profession_name}' not found.")
                        continue
                    for state_code, requirements in states.items():
                        country_code, _ = state_code.split("-")
                        country = session.query(CountryORM).filter_by(code=country_code).first()
                        state = session.query(StateORM).filter_by(abbreviation=state_code).first()
                        if not country or not state:
                            print(f"Country or state not found for code: {state_code}")
                            continue
                        for req in requirements:
                            existing = (
                                session.query(RequirementORM)
                                .filter_by(
                                    profession_id=profession.id,
                                    country_id=country.id,
                                    state_id=state.id,
                                    name=req["name"],
                                )
                                .first()
                            )
                            if existing:
                                print(f"Requirement {req['name']} for {state_code} already exists. Skipping.")
                                continue
                            allow_multiple = req.get("allow_multiple")
                            if allow_multiple is None:
                                allow_multiple = req["name"] not in ("ID", "CV", "ProofOfBerlinResponsibility")
                            session.add(RequirementORM(
                                id=str(uuid4()),
                                profession_id=profession.id,
                                country_id=country.id,
                                state_id=state.id,
                                name=req["name"],
                                description=req["description"],
                                optional=req["optional"],
                                translation_required=req["translation_required_if_not_german"],
                                fullfilled=req["fullfilled"],
                                allow_multiple=allow_multiple,
                            ))
                            print(f"Inserted default requirement '{req['name']}' for {state_code}.")
        except Exception as error:
            print(f"Error creating default requirements: {error}")

    @staticmethod
    def _as_tuple(orm_req: RequirementORM) -> tuple:
        return (
            orm_req.id,
            orm_req.profession_id,
            orm_req.country_id,
            orm_req.state_id,
            orm_req.name,
            orm_req.description,
            orm_req.optional,
            orm_req.translation_required,
            orm_req.fullfilled,
            orm_req.allow_multiple,
        )
