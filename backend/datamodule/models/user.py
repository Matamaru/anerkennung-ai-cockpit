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
            id = None):  
        """
        Initialize the user
        :param username: username
        :param password: password
        :param email: email
        :param salt: salt
        :param pepper: pepper
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
#            print(f"{self.username} is already in database.")
            logger.error("Username already in use")
            raise InsertError("Username already in use")
#        else:
#            print(f"{self.username} is not in database yet.")

        is_email, _ = User.email_in_db(self.email)
        if is_email:
#            print(f"{self.email} is already in database.")
            logger.error('Email already in use')
            raise InsertError('Email already in use')
#        else:
#            print(f"{self.email} is not in database yet.")

        if not self.valid_password(self.password):
#            print("Password not valid")
            logger.error('Password not valid')
            raise InsertError('Password not valid: Use at least 12 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character')

        if not self.valid_email(self.email):
#            print("Email not valid")
            logger.error('Email not valid')
            raise InsertError('Email not valid')

        try:
            db.connect()
            hashed_pwd_salted = User.generate_hashed_password(self.password, self.salt)
            hashed_pwd_peppered = User.generate_hashed_password(hashed_pwd_salted, self.pepper)
            # Make sure INSERT_USER uses RETURNING * if you want to fetch the inserted row!
            db.cursor.execute(
                INSERT_USER,
                (
                    self.username, 
                    hashed_pwd_peppered,
                    self.email, 
                    self.salt, 
                    self.pepper,
                    self.id
                )
            )
            tuple_data = db.cursor.fetchone()
            if tuple_data:    # Only set attributes if data is returned
                self.password = tuple_data[1]
                self.id = tuple_data[5]
#            print(f"User {self.username} successfully saved in database.")
            return tuple_data
        except DatabaseConnectionError as error:
#            print("DatabaseConnectionError")
            logger.error(error)
            raise
        except (Exception, psycopg2.DatabaseError) as error:
#            print("InsertError")
            logger.error(error)
            raise InsertError(error)
        finally:
            db.close_conn()           

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
        if is_user and user[5] != self.id:
            raise UpdateError('Username already in use')
        else:
            # in case user wants to update email
            # check if email is already in db
            # if yes, check if it is the same user
            is_email, user = User.email_in_db(self.email)
            if is_email and user[5] != self.id:
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
                        self.username = tuple_data[0]
                        self.password = tuple_data[1]
                        self.email = tuple_data[5]
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
        Checks if password sent to api is correct.
        :param password: password to check
        return: True if correct, False if not correct
        """
        is_peppered = (
            self.password == self.generate_hashed_password(password, self.pepper))
        return is_peppered
    
    ###================###
    ### flask-login methods ###
    ###================###
    def get_id(self):
        """
        Returns the id of the user.
        return: id of the user
        """
        return self.id
    
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
        if self.id:
            return False
        else:
            return True
    
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
    def select_by_id(id):
        """
        Gets user from database by id and creates user object.
        :param id: id to select user from db
        return: user object
        """
        db.connect()
        try:
            print(SELECT_USER_BY_ID)
            # db.cursor.execute(SQL_GET_USER_BY_ID, (self.id,))
            # user = db.cursor.fetchone()
            # return user
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def select_by_username(username):
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
        return User(*user_tuple)
    
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
        admin_email: str = admin_email):
        admin = User(username = admin_username,
                     password=admin_password,
                     email=admin_email)
        return admin    

def main():
    user = User(
        username='test_user',
        password='1A@test_password', 
        salt=None, 
        pepper=None,
        email='test@email.com',
        id=None)
    print(user.__dict__)
    user.insert()
    print(User.select_all(SELECT_ALL_USERS))
    user.delete()
    print(User.select_all(SELECT_ALL_USERS))



    

if __name__ == '__main__':
    main()