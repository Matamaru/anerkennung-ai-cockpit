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

from backend.datamodule.models.user_sql import CREATE_TABLE_USERS
from backend.datamodule.models.role_sql import CREATE_TABLE_ROLES

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
		self.cursor.execute("DROP TABLE IF EXISTS _users;")
		self.cursor.execute("DROP TABLE IF EXISTS _roles;")
		# Add more table drops as needed here
		print('Database tables dropped if existing.')


	def create_all_tables(self):
		"""Create necessary tables in the database."""
		# Create roles table, as it is needed for users table foreign key
		self.cursor.execute(CREATE_TABLE_ROLES)
		# Create users table	
		self.cursor.execute(CREATE_TABLE_USERS)			
		# Add more table creations as needed here
		print('Database tables created if not existing.')

	def execute_query(self, query, values=None):
		"""Execute a given SQL query with optional values."""
		try:
			self.cursor.execute(query, values)
			return self.cursor
		except (Exception, psycopg2.DatabaseError) as error:
			print(f"Error executing query: {error}")
			return None