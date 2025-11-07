import psycopg2
import os
import json
import logging
from dataclasses import dataclass

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