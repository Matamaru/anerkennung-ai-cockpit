#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:			backend.datamodule.datamodule 
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

#=== Imports

import psycopg2
import os
from dotenv import load_dotenv
from uuid import uuid4

from backend.datamodule.models.app_docs_sql import CREATE_TABLE_APP_DOCS
from backend.datamodule.models.application_sql import CREATE_TABLE_APPLICATION
from backend.datamodule.models.country_sql import CREATE_TABLE_COUNTRY
from backend.datamodule.models.file_type_sql import CREATE_TABLE_FILE_TYPE
from backend.datamodule.models.profession_sql import CREATE_TABLE_PROFESSION
from backend.datamodule.models.status_sql import CREATE_TABLE_STATUS
from backend.datamodule.models.user_sql import CREATE_TABLE_USERS
from backend.datamodule.models.role_sql import CREATE_TABLE_ROLES
from backend.datamodule.models.file_sql import CREATE_TABLE_FILE
from backend.datamodule.models.document_type_sql import CREATE_TABLE_DOCUMENT_TYPE
from backend.datamodule.models.document_data_sql import CREATE_TABLE_DOCUMENT_DATA
from backend.datamodule.models.document_sql import CREATE_TABLE_DOCUMENT
from backend.datamodule.models.state_sql import CREATE_TABLE_STATES
from backend.datamodule.models.requirements_sql import CREATE_TABLE_REQUIREMENTS

#=== Defs and classes

class DataBase:
	def __init__(self, params):
		self.params = params

	def connect(self):
		self.conn = psycopg2.connect(**self.params)
		self.cursor = self.conn.cursor()
		self.conn.autocommit = True

	def close_conn(self):
		if self.cursor is not None:
			self.cursor.close()
		if self.conn is not None:
			self.conn.close()
#		print('Connection to database closed.')

	def check_conn(self):
		if self.conn:
			print('Connection to database established.')
		else:
			print('No connection to database.') 

	def drop_all_tables(self):
		"""Drop all tables in the database."""
		self.cursor.execute("DROP TABLE IF EXISTS _users CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _roles CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _file_type CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _file CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _document_type CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _document_data CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _status CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _document CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _country CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _states CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _requirements CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _profession CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _application CASCADE;")
		self.cursor.execute("DROP TABLE IF EXISTS _app_docs CASCADE;")

		# Add more table drops as needed here
		print('Database tables dropped if existing.')


	def create_all_tables(self):
		"""Create necessary tables in the database."""
		
		#=== Users and Roles Tables
		# Create roles table, as it is needed for users table foreign key
		self.cursor.execute(CREATE_TABLE_ROLES)
		# Create users table	
		self.cursor.execute(CREATE_TABLE_USERS)

		#=== Document Related Tables	
		# create table file types
		self.cursor.execute(CREATE_TABLE_FILE_TYPE)
		# create file table
		self.cursor.execute(CREATE_TABLE_FILE)
		# create document_type table
		self.cursor.execute(CREATE_TABLE_DOCUMENT_TYPE)
		# create document_data table
		self.cursor.execute(CREATE_TABLE_DOCUMENT_DATA)
		# create status table
		self.cursor.execute(CREATE_TABLE_STATUS)
		# create document table
		self.cursor.execute(CREATE_TABLE_DOCUMENT)

		#=== Requirements Related Tables
		# create countries table
		self.cursor.execute(CREATE_TABLE_COUNTRY)
		# create states table
		self.cursor.execute(CREATE_TABLE_STATES)
		# create profession table
		self.cursor.execute(CREATE_TABLE_PROFESSION)	
		# create requirements table
		self.cursor.execute(CREATE_TABLE_REQUIREMENTS)

		#=== Application Related Tables
		# create application table	
		self.cursor.execute(CREATE_TABLE_APPLICATION)
		# create app_docs table
		self.cursor.execute(CREATE_TABLE_APP_DOCS)

		# Add more table creations as needed here
		
		#=== Final print
		print('Database tables created if not existing.')



	def execute_query(self, query, values=None):
		"""Execute a given SQL query with optional values."""
		try:
			self.cursor.execute(query, values)
			return self.cursor
		except (Exception, psycopg2.DatabaseError) as error:
			print(f"Error executing query: {error}")
			return None
