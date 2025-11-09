import psycopg2
import os
import json
import logging
from dataclasses import dataclass

from backend.datamodule import db

#=== Logger
# create logger path if not existing
log_dir = 'backend/datamodule/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)    

# Create a logger for the specific module
logger = logging.getLogger('basemodel')

# Set the desired log level (e.g., logging.DEBUG, logging.INFO, logging.WARNING, etc.)
logger.setLevel(logging.DEBUG)

# Create a handler for the logs (e.g., FileHandler, StreamHandler, etc.)
handler = logging.FileHandler('backend/datamodule/logs/models.log')

# Set the desired log format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Error handling
class DatabaseConnectionError(Exception):
    result = {}
    def __init__(self, error):
        self.error = error 
        self.result['error'] = self.error
        self.result['message'] = self.result['message'] + ': ' + str(self.error)
        logger.error(self.result['message'])
        return json.dumps(self.result)

class CreateTableError(Exception):
    logger.error('Create table error' + str(Exception))

class RecordNotFoundError(Exception):
    logger.error('Record not found' + str(Exception))
    #TODO: api response

class InsertError(Exception):
    logger.error('Insert error' + str(Exception))
    #TODO: api response

class UpdateError(Exception):
    logger.error('Update error' + str(Exception))
    #TODO: api response

class DeleteError(Exception):
    logger.error('Delete error' + str(Exception))
    #TODO: api response

# Base model
@dataclass
class Model(object):
    def __init__(self, *args, **kwargs):
        """
        Initialize the model
        :param args: tuple of arguments
        :param kwargs: dictionary of keyword arguments
        """
        for arg in args: 
            self.__dict__.update(arg)
        for key, value in kwargs.items():
            self.__dict__[key] = value
            
    def insert(self, sql_insert_model: str, values: tuple) -> int:
        """
        Insert a new row into the table
        :param sql: sql query
        :param values: values to insert
        :return: id of inserted row
        """
        try:
            db.connect()
        except (Exception, psycopg2.DatabaseError) as error:
            raise DatabaseConnectionError(error)
        finally:
            try:
                db.cursor.execute(sql_insert_model, values)
                # if RETURNING in sql sends id back, fetch id as tuple from db
                tuple_id = db.cursor.fetchone()
                # set self.id to id from db
                self.id = tuple_id[0]
                return self.id
            except (Exception, psycopg2.DatabaseError) as error:
                raise InsertError(error)
            finally:
                db.close_conn()

    def update(self, sql_update_model: str, values: tuple) -> tuple:
        """
        Update a row in the table
        :param sql: sql query
        :param values: values to update
        :return: tuple of updated row
        """
        db.connect()
        try:
            db.cursor.execute(sql_update_model, values)
            # if RETURNING in sql sends updated back, 
            # fetch data as tuple from db
            tuple_data = db.cursor.fetchone()
            # set all data from db to self
            self.__dict__.update(tuple_data)
            return tuple_data
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    def delete(self, sql_delete_model: str, value: tuple) -> int:
        """
        Delete a row from the table
        :param sql: sql query   
        :param value: value to identify row to delete
        :return: id of deleted row
        """
        db.connect()
        try:
            db.cursor.execute(sql_delete_model, value)
            return value[0]
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    def to_tuple(self) -> tuple:
        """
        Convert model to tuple
        :return: tuple
        """
        return tuple(self.__dict__.values())
    
    def to_json(self):
        """
        Convert model to json
        :return: json
        """
        return json.dumps(self.__dict__)
            
    ### static methods ###
    @staticmethod
    def select_all(sql_select_model: str) -> tuple:
        db.connect()
        try:
            db.cursor.execute(sql_select_model)
            result = db.cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def select_columns(sql_select_model: str, values: tuple) -> tuple:
        db.connect()
        try:
            db.cursor.execute(sql_select_model, values)
            result = db.cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()

    @staticmethod
    def select_where_column_equals(
            sql_select_model: str, 
            column: str, 
            value: str) -> tuple:
        try:
            db.connect()
        except (Exception, psycopg2.DatabaseError) as error:    
            raise DatabaseConnectionError(error)
        finally:
            try:
                sql = sql_select_model + f" WHERE {column} = %s"
                db.cursor.execute(sql, (value,))
                result = db.cursor.fetchall()
                return result
            except (Exception, psycopg2.DatabaseError) as error:
                print(error)
            finally:
                db.close_conn()

    @staticmethod
    def select_where_column_like(
            sql_select_model: str, 
            column: str, 
            value: str) -> tuple:
        db.connect()
        try:
            sql = sql_select_model + f" WHERE {column} LIKE %s"
            db.cursor.execute(sql, (value,))
            result = db.cursor.fetchall()
            return result
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            db.close_conn()