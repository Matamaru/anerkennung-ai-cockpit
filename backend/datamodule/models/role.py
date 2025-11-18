#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.role                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports
from uuid import uuid4
from dataclasses import dataclass

from backend.datamodule.models.basemodel import *
from backend.datamodule import db
from backend.datamodule.models.role_sql import *

 
#=== defs and classes
@dataclass
class Role(Model):
    """
    Role model class
    
    Attributes:
        role_id (str): Unique identifier for the role.
        role_name (str): Name of the role.
        description (str): Description of the role.
    """
    
    def __init__(self, role_name: str, description: str, role_id: str = None):
        super().__init__()
        self.role_name = role_name
        self.description = description
        if role_id:
            self.role_id = role_id
        else:
            self.role_id = str(uuid4())
    
    def to_json(self) -> dict:
        """
        Convert Role object to JSON serializable dictionary.
        
        Returns:
            dict: JSON serializable representation of the Role object.
        """
        role_json = {
            "role_name": self.role_name,
            "description": self.description,
            "role_id": self.role_id,
        }
        return role_json
    
    def insert(self):
        """
        Insert Role object into the database.
        
        Returns:
            tuple: Result of the insert operation.
        """
        values = (
            self.role_id,
            self.role_name,
            self.description
        )
        try:
            db.connect()
            db.cursor.execute(INSERT_ROLE, values)
            tuple_data = db.cursor.fetchone()
            if tuple_data:
                self.role_id = tuple_data[0]
#                print(f"Role {self.role_name} inserted.")
            return tuple_data
        except DatabaseConnectionError as error:
#            print(f"Database connection error: {error}")
            return None
        finally:
            db.close_conn()
        

    def update(self):
        """
        Update Role object in the database.
        
        Returns:
            tuple: Result of the update operation.
        """
        values = (
            self.role_id,
            self.role_name,
            self.description
        )
        try:
            db.connect()
            db.cursor.execute(UPDATE_ROLE, values)
            tuple_data = db.cursor.fetchone()
            if tuple_data:
                self.role_id = tuple_data[0]
                self.role_name = tuple_data[1]
                self.description = tuple_data[2]
            return tuple_data       
        except DatabaseConnectionError as error:
            print(f"Database connection error: {error}")
            return None
        finally:
            db.close_conn()

    @staticmethod
    def from_json(data: dict):
        """
        Create Role object from JSON dictionary.
        
        Args:
            data (dict): JSON dictionary containing role data.  
        
        Returns:
            Role: Role object created from the JSON data.
        """
        return Role(
            role_name=data.get("role_name"),
            description=data.get("description"),
            role_id=data.get("role_id")
        )
    
    @staticmethod
    def from_tuple(data: tuple):
        """
        Create Role object from database tuple.
        
        Args:
            data (tuple): Tuple containing role data from the database.
        Returns:
            Role: Role object created from the database tuple.
        """
        return Role(
            role_name=data[1],
            description=data[2],
            role_id=data[0]
        )   
    
    @staticmethod
    def get_all_roles():
        """
        Get all roles from the database.
        
        Returns:
            list: List of all Role objects.
        """
        results = db.execute_query(SELECT_ALL_ROLES)
        roles = [Role.from_tuple(row) for row in results]
        return roles
    
    @staticmethod
    def get_by_role_name(role_name: str):
        """
        Get Role object by role name.
        
        Args:
            role_name (str): Name of the role to retrieve.
        
        Returns:
            Role: Role object with the specified role name, or None if not found.
        """
        values = (f"%{role_name}%",)
        try:
            db.connect()
            db.cursor.execute(SEARCH_ROLE_BY_NAME, values)
            tuple_data = db.cursor.fetchone()
            if tuple_data:
#                print(tuple_data)
                return Role.from_tuple(tuple_data)
            else:
                print("No role found")
                return None
        except DatabaseConnectionError as error:
            print(f"Database connection error: {error}")
            return None
        finally:
            db.close_conn()

        
    @staticmethod
    def get_by_role_id(role_id: str):
        """
        Get Role object by role ID.
        
        Args:
            role_id (str): ID of the role to retrieve.
        
        Returns:
            Role: Role object with the specified role ID, or None if not found.
        """
        values = (role_id,)
        try:
            db.connect()
            db.cursor.execute(SELECT_ROLE_BY_ID, values)
            tuple_data = db.cursor.fetchone()
            if tuple_data:
                return Role.from_tuple(tuple_data)
            else:
                return None
        except DatabaseConnectionError as error:
            print(f"Database connection error: {error}")
            return None
        finally:
            db.close_conn()

    @staticmethod
    def create_default_roles():
        """
        Ensure default roles exist in the database.
        """
        # Define default roles
        default_roles = [
            Role(role_name="candidate", description="Standard user with permission to access own data."),
            Role(role_name="admin", description="Administrator with all access permissions."),
            Role(role_name="recruiter", description="User with permission to manage candidate data.")
        ]

#        print([role.to_json() for role in default_roles])

        # Check and insert missing roles
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
