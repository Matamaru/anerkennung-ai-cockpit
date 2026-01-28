#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.role                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

from uuid import uuid4
from dataclasses import dataclass

from backend.datamodule.models.basemodel import *
from backend.datamodule.orm import Role as RoleORM
from backend.datamodule.sa import session_scope


@dataclass
class Role(Model):
    def __init__(self, role_name: str, description: str, role_id: str = None):
        super().__init__()
        self.role_name = role_name
        self.description = description
        self.role_id = role_id or str(uuid4())
    
    def to_json(self) -> dict:
        return {
            "role_name": self.role_name,
            "description": self.description,
            "role_id": self.role_id,
        }
    
    def insert(self):
        values = (
            self.role_id,
            self.role_name,
            self.description
        )
        try:
            with session_scope() as session:
                orm_role = RoleORM(role_id=self.role_id, role_name=self.role_name, description=self.description)
                session.add(orm_role)
                session.flush()
                self.role_id = orm_role.role_id
                return Role._as_tuple(orm_role)
        except Exception as error:
            raise InsertError(error)
        
    def update(self):
        values = (
            self.role_id,
            self.role_name,
            self.description
        )
        try:
            with session_scope() as session:
                orm_role = session.query(RoleORM).filter_by(role_id=self.role_id).first()
                if not orm_role:
                    raise UpdateError("Role not found")
                orm_role.role_name = self.role_name
                orm_role.description = self.description
                session.flush()
                return Role._as_tuple(orm_role)
        except Exception as error:
            raise UpdateError(error)

    @staticmethod
    def from_json(data: dict):
        return Role(
            role_name=data.get("role_name"),
            description=data.get("description"),
            role_id=data.get("role_id")
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        return Role(
            role_name=data[1],
            description=data[2],
            role_id=data[0]
        )   
    
    @staticmethod
    def get_all_roles():
        with session_scope() as session:
            roles = session.query(RoleORM).all()
            return [Role.from_tuple(Role._as_tuple(r)) for r in roles]
    
    @staticmethod
    def get_by_role_name(role_name: str):
        with session_scope() as session:
            orm_role = session.query(RoleORM).filter(RoleORM.role_name.ilike(f"%{role_name}%")).first()
            return Role.from_tuple(Role._as_tuple(orm_role)) if orm_role else None

    @staticmethod
    def get_by_role_id(role_id: str):
        with session_scope() as session:
            orm_role = session.query(RoleORM).filter_by(role_id=role_id).first()
            return Role.from_tuple(Role._as_tuple(orm_role)) if orm_role else None

    @staticmethod
    def get_role_id_by_name(role_name: str):
        role = Role.get_by_role_name(role_name)
        return role.role_id if role else None

    @staticmethod
    def create_default_roles():
        default_roles = [
            Role(role_name="candidate", description="Standard user with permission to access own data."),
            Role(role_name="admin", description="Administrator with all access permissions."),
            Role(role_name="recruiter", description="User with permission to manage candidate data.")
        ]

        for role in default_roles:
            existing_role = Role.get_by_role_name(role.role_name)
            if not existing_role:
                print(f"Creating default role: {role.role_name} ...")
                try:
                    role_tuple = role.insert()
                    print(f"Role {role_tuple[1]} created.")
                except InsertError as error:
                    print(f"Error creating role {role.role_name}: {error}")
            else:
                print(f"Role {role.role_name} already exists.")

    @staticmethod
    def _as_tuple(orm_role: RoleORM) -> tuple:
        return (orm_role.role_id, orm_role.role_name, orm_role.description)
