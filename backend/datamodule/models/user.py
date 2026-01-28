#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.user                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

from uuid import uuid4
from dataclasses import dataclass
import logging
from flask_login import UserMixin
import os
from dotenv import load_dotenv

from backend.datamodule.models.basemodel import *
from backend.utils.creds import Creds
from backend.datamodule.orm import Role as RoleORM, User as UserORM
from backend.datamodule.sa import session_scope
from backend.datamodule.models.role import Role

#=== Load environment variables
load_dotenv()
admin_username = os.getenv('ADMIN_USERNAME', 'admin')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
admin_email = os.getenv('ADMIN_EMAIL', 'admin@admin.de')

#=== Logger

logger = logging.getLogger('user')
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('backend/datamodule/logs/user.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

#=== Globals

creds = Creds()


class User(Model, UserMixin):
    def __init__(
            self, 
            username: str, 
            password: str,
            email: str, 
            salt = None, 
            pepper = None,
            role_id: str = None,
            role_name: str = None,
            b_admin: bool = False, 
            id = None):  
        """
        Initialize the user.
        """    
        super().__init__()  
        self.username = username
        self.password = password
        self.email = email
        self.salt = salt or self.make_salt()
        self.pepper = pepper or self.make_salt()
        self.role_id = role_id or None
        self.role_name = role_name or (Role.get_by_role_id(role_id).role_name if role_id else None)
        self.b_admin = b_admin if b_admin else False
        self.id = id or uuid4().hex

    def insert(self) -> tuple:
        """
        Checks valid user data and inserts valid user into the database.
        Return: tuple of the user or None, if error
        """
        is_user, _ = User.username_in_db(self.username)
        if is_user:
            logger.error("Username already in use")
            raise InsertError("Username already in use")

        is_email, _ = User.email_in_db(self.email)
        if is_email:
            logger.error('Email already in use')
            raise InsertError('Email already in use')

        if not self.valid_password(self.password):
            logger.error('Password not valid')
            raise InsertError('Password not valid')

        if not self.valid_email(self.email):
            logger.error('Email not valid')
            raise InsertError('Email not valid')

        if self.role_id is None:
            with session_scope() as session:
                role_candidate = session.query(RoleORM).filter_by(role_name='candidate').first()
                if role_candidate:
                    self.role_id = role_candidate.role_id
                else:
                    logger.error('Default role candidate not found')
                    raise InsertError('Default role candidate not found')

        hashed_pwd_salted = User.generate_hashed_password(self.password, self.salt)
        hashed_pwd_peppered = User.generate_hashed_password(hashed_pwd_salted, self.pepper)

        try:
            with session_scope() as session:
                orm_user = UserORM(
                    user_id=self.id,
                    role_id=self.role_id,
                    username=self.username,
                    password=hashed_pwd_peppered,
                    email=self.email,
                    b_admin=self.b_admin,
                    salt=self.salt,
                    pepper=self.pepper,
                )
                session.add(orm_user)
                session.flush()
                self.password = orm_user.password
                self.id = orm_user.user_id
                role = session.query(RoleORM).filter_by(role_id=self.role_id).first()
                self.b_admin = (role.role_name == 'admin') if role else False
                tuple_data = User._as_tuple(orm_user)
                logger.debug(f"User data inserted successfully: {tuple_data}")
                return tuple_data
        except Exception as error:
            logger.error(f"Error inserting user: {error}")
            raise InsertError(error)

    def update(self, values: tuple) -> tuple:
        """
        Checks valid user data and updates valid user into the database.
        return: tuple of the user
        """
        is_user, user = User.username_in_db(self.username)
        if is_user and user[0] != self.id:
            raise UpdateError('Username already in use')

        is_email, user = User.email_in_db(self.email)
        if is_email and user[0] != self.id:
            logger.error('Email already in use')
            raise UpdateError('Email already in use')

        try:
            with session_scope() as session:
                orm_user = session.query(UserORM).filter_by(user_id=self.id).first()
                if not orm_user:
                    raise UpdateError('User not found')
                (
                    role_id,
                    username,
                    password,
                    email,
                    b_admin,
                    salt,
                    pepper,
                    user_id,
                ) = values
                orm_user.role_id = role_id
                orm_user.username = username
                orm_user.password = password
                orm_user.email = email
                orm_user.b_admin = b_admin
                orm_user.salt = salt
                orm_user.pepper = pepper
                session.flush()
                self.role_id = orm_user.role_id
                self.username = orm_user.username
                self.password = orm_user.password
                self.email = orm_user.email
                role = session.query(RoleORM).filter_by(role_id=self.role_id).first()
                self.is_admin = (role.role_name == 'admin') if role else False
                return User._as_tuple(orm_user)
        except Exception as error:
            logger.error(error)
            raise UpdateError(error)

    def delete(self) -> int:
        """
        Deletes user from database.
        return: number of deleted row as int
        """
        try:
            with session_scope() as session:
                deleted = session.query(UserORM).filter_by(user_id=self.id).delete()
                return deleted
        except Exception as error:
            logger.error(error)
            raise DeleteError(error)

    def valid_password(self, password) -> bool:
        return creds.check_valid_password(password)['b_valid']
    
    def valid_email(self, email) -> bool:
        return creds.check_valid_email(email)['b_valid']
    
    def check_password(self, password):  
        result = creds.check_hashed_password(
            login_password=password,
            db_password=self.password,
            db_salt=self.salt,
            db_pepper=self.pepper)
        return result

    ### flask-login methods ###
    def get_id(self):
        return str(self.id)
    
    def is_active(self):
        return bool(self.id)
    
    def is_authenticated(self):
        return bool(self.id)
        
    def is_anonymous(self):
        return self.id is None

    #=== Role check methods
    def is_admin(self) -> bool:
        if self.is_admin:
            role = Role.get_by_role_id(self.role_id)
            return bool(role and role.role_name == 'admin')
        return False

    def is_candidate(self) -> bool:
        if self.role_id:
            role = Role.get_by_role_id(self.role_id)
            return bool(role and role.role_name == 'candidate')
        return False
        
    def is_recruiter(self) -> bool:
        if self.role_id:
            role = Role.get_by_role_id(self.role_id)
            return bool(role and role.role_name == 'recruiter')
        return False

    ### STATIC METHODS ###
    @staticmethod
    def make_salt():
        return creds.make_salt()

    @staticmethod
    def username_in_db(username):
        with session_scope() as session:
            orm_user = session.query(UserORM).filter_by(username=username).first()
            if orm_user:
                return True, User._as_tuple(orm_user)
            return False, None

    @staticmethod
    def email_in_db(email) -> bool:
        with session_scope() as session:
            orm_user = session.query(UserORM).filter_by(email=email).first()
            if orm_user:
                return True, User._as_tuple(orm_user)
            return False, None

    @staticmethod
    def delete_by_username(username):
        user = User.get_by_username(username)
        if user:
            try:
                with session_scope() as session:
                    session.query(UserORM).filter_by(username=username).delete()
            except Exception as error:
                logger.error(error)
                raise DeleteError(error)
        else:
            logger.error('User not found')
            raise DeleteError('User not found')
            
    @staticmethod
    def get_by_id(id):
        with session_scope() as session:
            orm_user = session.query(UserORM).filter_by(user_id=id).first()
            return User._as_tuple(orm_user) if orm_user else None

    @staticmethod
    def get_by_username(username):
        with session_scope() as session:
            orm_user = session.query(UserORM).filter_by(username=username).first()
            return User._as_tuple(orm_user) if orm_user else None

    @staticmethod
    def get_all_users():
        with session_scope() as session:
            users = session.query(UserORM).all()
            return [User._as_tuple(u) for u in users]

    @staticmethod
    def generate_hashed_password(password, salt):
        return creds.generate_hashed_password(password, salt)
    
    @staticmethod
    def from_tuple(user_tuple):
        return User(
            id = user_tuple[0],
            role_id = user_tuple[1],
            username = user_tuple[2],
            password = user_tuple[3],
            email = user_tuple[4],
            b_admin = user_tuple[5],
            salt = user_tuple[6],
            pepper = user_tuple[7]
        )
    
    @staticmethod
    def from_dict(user_dict):
        return User(**user_dict)

    @staticmethod
    def create_admin(
        admin_username: str = admin_username,
        admin_password: str = admin_password,
        admin_email: str = admin_email,
        admin_b_admin: bool = True):
        admin_role_id = Role.get_by_role_name('admin').role_id
        admin = User(
            role_id=admin_role_id,
            username=admin_username,
            password=admin_password,
            email=admin_email,
            b_admin=admin_b_admin)
        return admin

    @staticmethod
    def _as_tuple(orm_user: UserORM) -> tuple:
        return (
            orm_user.user_id,
            orm_user.role_id,
            orm_user.username,
            orm_user.password,
            orm_user.email,
            orm_user.b_admin,
            orm_user.salt,
            orm_user.pepper,
        )
