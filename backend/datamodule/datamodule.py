#****************************************************************************
#   Application:    Annerkennung Ai Cockpit
#   Module:			backend.datamodule.datamodule 
#	Author:			Heiko Matamaru, IGS         							
#	Version:		0.0.1									                
#****************************************************************************

#=== Imports

import psycopg2
from backend.datamodule.models.user_sql import CREATE_TABLE_USERS

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
		print('Connection to database closed.')

	def check_conn(self):
		if self.conn:
			print('Connection to database established.')
		else:
			print('No connection to database.') 

	def create_tables(self):
		"""Create necessary tables in the database."""
		self.cursor.execute(CREATE_TABLE_USERS)			
		print('Database tables created if not existing.')
		# Add more table creations as needed here


	