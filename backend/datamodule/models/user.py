#****************************************************************************
#		Module:		backend.datamodule.models.user (Anerkennung AI Cockpit)	*
#		Author:		Heiko Matamaru, IGS 						            *
#		Version:	0.0.1										            *
#****************************************************************************

#=== Imports

import psycopg2

from uuid import uuid4
from dataclasses import dataclass
import logging

from backend.datamodule.models.basemodel import *
from backend.datamodule import db
from backend.utils.creds import Creds
from backend.datamodule.models.user_sql import *


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

class User(Model):
    def __init__(self, username, password, salt, pepper, email, id):  
        """
        Initialize the user
        :param username: username
        :param password: password
        :param salt: salt
        :param pepper: pepper
        :param email: email
        :param id: id
        """    
        super().__init__()  
        self.username = username
        self.password = password
        if salt:
            self.salt = salt
        else:
            self.salt = self.make_salt()
        if pepper:
            self.pepper = pepper
        else:
            self.pepper = self.make_salt()
        self.email = email
        if id:
            self.id = id
        else:
            self.id = uuid4().hex

    def insert(self) -> tuple:
        """
        Checks valid user data and inserts valid user into the database.
        return: tuple of the user
        """
        is_user, user = User.username_in_db(self.username)
        # check if username already in db
        if is_user:
            # check if email already in db
            is_email, user = User.email_in_db(self.email)
            if is_email:
                logger.error('Email already in use')
                raise InsertError('Email already in use')           
            else:
                # check if password is valid
                if not self.valid_password(self.password):
                    logger.error('Password not valid')
                    raise InsertError('Password not valid: Use at least 12 characters, 1 uppercase, 1 lowercase, 1 number, 1 special character')
                else:
                    # check if email is valid
                    if not self.valid_email(self.email):
                        logger.error('Email not valid')
                        raise InsertError('Email not valid')
                    else:
                        # check if db connection is valid
                        try:
                            db.connect() 
                        except DatabaseConnectionError as error:
                            logger.error(error)
                            raise DatabaseConnectionError(error)
                        finally:
                            # insert user into db
                            try:
                                hashed_pwd_salted = User.generate_hashed_password(
                                    self.password, self.salt)
                                hashed_pwd_peppered = User.generate_hashed_password(
                                    hashed_pwd_salted, self.pepper)
                                db.cursor.execute(
                                    INSERT_USER, (
                                        self.username, 
                                        hashed_pwd_peppered,
                                        self.email, 
                                        self.salt, 
                                        self.pepper,
                                        self.id))
                                tuple_data = db.cursor.fetchone()
                                # set changed data to user
                                self.password = tuple_data[1]
                                self.id = tuple_data[5]
                                return tuple_data
                            except (Exception, psycopg2.DatabaseError) as error:
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
        return creds.check_secure_password(password)['b_secure']
    
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
            SELECT_USER_BY_USERNAME, 
            'username', 
            username)
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