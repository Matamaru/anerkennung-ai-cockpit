#****************************************************************************
#   Application:	Anerkennung AI Cockpit							        *
#	Module:		    backend.datamodule.models.user                          *
#	Author:		    Heiko Matamaru, IGS    						            *
#	Version:	    0.0.1									                *
#****************************************************************************

#=== Imports

import psycopg2

from uuid import uuid4
from dataclasses import dataclass
import logging
from flask_login import UserMixin
import os
from dotenv import load_dotenv

from backend.datamodule.models.basemodel import *
from backend.utils.creds import Creds
from backend.datamodule.models.user_sql import *
from backend.datamodule import db
from backend.datamodule.models.role import Role

#=== Load environment variables
load_dotenv()
admin_username = os.getenv('ADMIN_USERNAME', 'admin')
admin_password = os.getenv('ADMIN_PASSWORD', 'admin')
admin_email = os.getenv('ADMIN_EMAIL', 'admin@admin.de')

#=== Logger

# Create a logger for the specific module
logger = logging.getLogger('user')

# Set the desired log level (e.g., logging.DEBUG, logging.INFO, logging.WARNING, etc.)
logger.setLevel(logging.DEBUG)

# Create a handler for the logs (e.g., FileHandler, StreamHandler, etc.)
handler = logging.FileHandler('backend/datamodule/logs/user.log')

# Set the desired log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

#=== Globals

creds = Creds()

#=== defs and classes

class User(Model, UserMixin):
    def __init__(
            self, 
            username: str, 
            password: str,
            email:str, 
            salt = None, 
            pepper = None,
            role_id: str = None,
            role_name: str = None,
            b_admin: bool = False, 
            id = None):  
        """
        Initialize the user
        :param username: username
        :param password: password
        :param email: email
        :param salt: salt
        :param pepper: pepper
        :param role_id: role_id
        :param role_name: role_name
        :param b_admin: b_admin
        :param id: id
        """    
        super().__init__()  
        self.username = username
        self.password = password
        self.email = email
        if salt:
            self.salt = salt
        else:
            self.salt = self.make_salt()
        if pepper:
            self.pepper = pepper
        else:
            self.pepper = self.make_salt()
        if role_id:
            self.role_id = role_id
        else:
            self.role_id = None
        if role_name:
            self.role_name = role_name
        else:
            self.role_name = Role.get_by_role_id(role_id).role_name if role_id else None 
        if b_admin:
            self.b_admin = b_admin
        else:
            self.b_admin = False
        if id:
            self.id = id
        else:
            self.id = uuid4().hex


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
            # assign default role 'candidate' to new user
            role_candidate = Role.get_by_role_name('candidate')
            if role_candidate:
                self.role_id = role_candidate.role_id
            else:
                logger.error('Default role candidate not found')
                raise InsertError('Default role candidate not found')

        try:
            db.connect()
            # generate hashed password with salt and pepper
            hashed_pwd_salted = User.generate_hashed_password(self.password, self.salt)
            hashed_pwd_peppered = User.generate_hashed_password(hashed_pwd_salted, self.pepper)
            # create values tuple for insert
            values = (
                self.id,
                self.role_id,
                self.username,
                hashed_pwd_peppered,
                self.email,
                self.b_admin,
                self.salt,
                self.pepper
            )
            # insert user into db
            db.cursor.execute(INSERT_USER, values)
            tuple_data = db.cursor.fetchone()

            # Check if data was returned from the query
            if tuple_data:
                logger.debug(f"User data inserted successfully: {tuple_data}")
                self.password = tuple_data[3]  # Assuming password is at index 3
                self.id = tuple_data[0]  # Assuming ID is at index 0
                # set b_admin from tuple_data via role_id
                if Role.get_by_role_id(self.role_id):
                    self.b_admin = (Role.get_by_role_id(self.role_id).role_name == 'admin')
                else:
                    self.b_admin = False
            else:
                logger.error("No data returned after user insert")
                raise InsertError("No data returned after insert query")

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Error inserting user: {error}")
            raise InsertError(error)

        finally:
            db.close_conn()
            return tuple_data

    def update(self, values: tuple) -> tuple:
        """
        Checks valid user data and updates valid user into the database.
        return: tuple of the user
        """
        # username is unique, check if username is already in db
        is_user, user = User.username_in_db(self.username)
        # in case user wants to update username
        # check if username is already in db
        # if yes, check if it is the same user
        # print(f'is_user: {is_user}\nuser: {user}')
        if is_user and user[0] != self.id:
            raise UpdateError('Username already in use')
        else:
            # in case user wants to update email
            # check if email is already in db
            # if yes, check if it is the same user
            is_email, user = User.email_in_db(self.email)
            if is_email and user[0] != self.id:
                logger.error('Email already in use')
                raise UpdateError('Email already in use')
            else:
                try:
                    db.connect()
                except DatabaseConnectionError as error:    
                    logger.error(error)     
                    raise DatabaseConnectionError(error)
                finally:
                    try:
                        db.cursor.execute(UPDATE_USER, values)
                        # if RETURNING in sql sends updated back, 
                        # fetch data as tuple from db
                        tuple_data = db.cursor.fetchone()
                        # set all data from db to self
                        self.role_id = tuple_data[1]
                        self.username = tuple_data[2]
                        self.password = tuple_data[3]
                        self.email = tuple_data[4]
                        if Role.get_by_role_id(self.role_id):
                            self.is_admin = (Role.get_by_role_id(self.role_id).role_name == 'admin')
                        else:
                            self.is_admin = False
                        # salt, pepper and id should not be updated
                        return tuple_data
                    except (Exception, psycopg2.DatabaseError) as error:
                        logger.error(error)
                        raise UpdateError(error)
                    finally:
                        db.close_conn()

    def delete(self) -> int:
        """
        Deletes user from database.
        return: number of deleted row as int
        """
        try:
            db.connect()
        except DatabaseConnectionError as error:
            logger.error(error)
            raise DatabaseConnectionError(error)
        finally:
            try:
                db.cursor.execute(DELETE_USER, (self.id,))
                deleted_row = db.cursor.rowcount
                # print(f'deleted_rows: {deleted_row}')
                return deleted_row
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                raise DeleteError(error)
            finally:
                db.close_conn()

    def valid_password(self, password) -> bool:
        """
        Checks if password is valid.
        return: True if valid, False if not valid
        """
        return creds.check_valid_password(password)['b_valid']
    
    def valid_email(self, email) -> bool:
        """
        Checks if email is valid.
        return: True if valid, False if not valid
        """
        return creds.check_valid_email(email)['b_valid']
    
    def check_password(self, password):  
        """
        Checks if password sent to database is correct.
        :param password: password to check
        return: True if correct, False if not correct
        """
        result = creds.check_hashed_password(
            login_password = password,
            db_password = self.password,
            db_salt = self.salt,
            db_pepper = self.pepper)
        return result
    

    
    ###================###
    ### flask-login methods ###
    ###================###
    def get_id(self):
        """
        Returns the id of the user.
        return: id of the user
        """
        return str(self.id)
    
    def is_active(self):
        """
        This property should return True if this is an active user - in addition to being authenticated, they also have activated their account, not been suspended, or any condition your application has for rejecting an account. Inactive accounts may not log in (without being forced of course).
        """
        if self.id:
            return True
        else:
            return False    
    
    def is_authenticated(self):
        """
        This property should return True if the user is authenticated, i.e. they have provided valid credentials. (Only authenticated users will fulfill the criteria of login_required.)
        """
        if self.id:
            return True
        else:
            return False
        
    def is_anonymous(self):
        """
        This property should return True if this is an anonymous user. (Actual users should return False instead.)
        """
        return self.id is None

#    @login_manager.user_loader
#    def load_user(user_id: str):
#        """
#        Given a user_id (stored in the session), return a User object
#        or None if not found.
#        Flask-Login calls this automatically.
#        """
#        try:
#            # if your primary key is int, cast here
#            user_tuple = User.get_by_id(user_id)
#        except (ValueError, TypeError):
#            return None
#    
#        if user_tuple is None:
#            return None
#    
#        return User.from_tuple(user_tuple)
#=== Role check methods

    def is_admin(self) -> bool:
        """
        Checks if user is admin.
        return: True if admin, False if not admin
        """
        if self.is_admin:
            #get role from role_id
            role = Role.get_by_role_id(self.role_id)
            if role and role.role_name == 'admin':
                return True
            else:
                return False
        else:
            return False

    def is_candidate(self) -> bool:
        """
        Checks if user is candidate.
        return: True if candidate, False if not candidate
        """
        if self.role_id:
            role = Role.get_by_role_id(self.role_id)
            if role and role.role_name == 'candidate':
                return True
            else:
                return False
        else:
            return False
        
    def is_recruiter(self) -> bool:
        """
        Checks if user is recruiter.
        return: True if recruiter, False if not recruiter
        """
        if self.role_id:
            role = Role.get_by_role_id(self.role_id)
            if role and role.role_name == 'recruiter':
                return True
            else:
                return False
        else:
            return False


    ###================###
    ### STATIC METHODS ###
    ###================### 
    @staticmethod
    def make_salt():
        """
        Creates salt.
        return: salt as string
        """
        return creds.make_salt()

    @staticmethod
    def username_in_db(username):
        """
        Checks if username is already in database.
        :param username: username to check
        return: True and userdata as tuple if username is in db, False and None if not
        """
        # get list of user_tuples
        user = User.select_where_column_equals(
            sql_select_model = SELECT_ALL_USERS, 
            column = 'username', 
            value = username)
        if user:
            return True, user[0]
        else:
            return False, None

    @staticmethod
    def email_in_db(email) -> bool:
        """
        Checks if email is already in database.
        :param email: email to check
        return: True and userdata as tuple if email is in db, False and None if not
        """
        user = User.select_where_column_equals(
            SELECT_USER_BY_EMAIL,
            'email',
            email)
        if user:
            return True, user[0]
        else:
            return False, None

    @staticmethod
    def delete_by_username(username):
        """
        Deletes user from database by username.
        :param username: username to delete
        return: deleted row data as tuple
        """
        try:
            db.connect()
        except DatabaseConnectionError as error:
            logger.error(error)
            raise DatabaseConnectionError(error)
        finally:
            user = User.get_by_username(username)
            if user:
                try:
                    # TODO: implement database functionality
                    #print(SQL_DELETE_USER_BY_USERNAME)
                    db.cursor.execute(DELETE_USER_BY_USERNAME, (username,))
                    deleted_rows = db.cursor.rowcount

                    # db.conn.commit()

                    # db.cursor.close()

                    # return deleted_rows
                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(error)
                    raise DeleteError(error)
                finally:
                    db.close_conn()
            else:
                logger.error('User not found')
                raise DeleteError('User not found')
            
    @staticmethod
    def get_by_id(id):
        """
        Gets user from database by id and creates user object.
        :param id: id to select user from db
        return: user object
        """
        db.connect()
        try:
            db.cursor.execute(SELECT_USER_BY_ID, (id,))
            user = db.cursor.fetchone()
            return user
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_by_username(username):
        """
        Gets user from database by username and creates user object.
        :param username: username to select user from db
        return: user object
        """
        db.connect()

        try:
            # print(SQL_GET_USER_BY_USERNAME)
            db.cursor.execute(SELECT_USER_BY_USERNAME, (username,))
            user = db.cursor.fetchone()
            db.conn.commit()
            return user
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def get_all_users():
        """
        Gets all users from database.
        return: list of user objects
        """
        db.connect()
        try:
            db.cursor.execute(SELECT_ALL_USERS)
            users = db.cursor.fetchall()
            return users
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def generate_hashed_password(password, salt):
        """
        Generates hashed password.
        :param password: password to hash
        :param salt: salt to hash password with
        return: hashed password
        """
        return creds.generate_hashed_password(password, salt)
    
    @staticmethod
    def from_tuple(user_tuple):
        """
        return: User object from tuple
        """
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
        """
        return: User object from dict
        """
        return User(**user_dict)

    @staticmethod
    def create_admin(
        admin_username: str = admin_username,
        admin_password: str = admin_password,
        admin_email: str = admin_email,
        admin_b_admin: bool = True):
        """
        Creates an admin user object with default or provided credentials.
        :param admin_username: Username for the admin user.
        :param admin_password: Password for the admin user.
        :param admin_email: Email for the admin user.
        :param admin_b_admin: Boolean flag indicating if the user is an admin.
        :return: User object representing the admin user.
        """
        admin_role_id = Role.get_by_role_name('admin').role_id
        admin = User(
            role_id=admin_role_id,
            username = admin_username,
            password=admin_password,
            email=admin_email,
            b_admin=admin_b_admin)
        return admin    
