#****************************************************************************
#		Module:		backend.datamodule.models.user (Anerkennung AI Cockpit)	*
#		Author:		Heiko Matamaru, IGS 						            *
#		Version:	0.0.1										            *
#****************************************************************************

#=== Imports

from uuid import uuid4

#=== defs and classes

class User():
	def __init__(self, 
			  username: str,
			  password: str, 
			  email: str,
			  salt: str,
			  pepper: str,
			  user_id: str):
		"""
		Initialize the user
		:param username: str
		:param password: str
		:param email: str
		:param salt: str
		:param pepper: str
		:param user_id: str
		"""
		self.username = username
		self.password = password
		self.email = email
		self.salt = salt
		self.pepper = pepper
		self.user_id = user_id


#=== main