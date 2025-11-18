#********************************************************************
#	Module:		backend.utils.creds.creds (Anerkennung AI Cockpit)	*
#	Author:		Heiko Matamaru, IGS             					*
#	Version:	0,0,1							                    *
#********************************************************************

#=== Imports

import string
import random
import re
import hashlib
import os
import base64

#=== defs and classes

class Creds:
	"""
	Creds handles all kinds of credentials for websites. Credentials are combinations of username and/or email address and a password with salt and pepper.
	"""

	# list alphabet (lowercase)
	l_alpha = list(string.ascii_lowercase)

	# list capitalized alphabet (uppercase)
	l_cap_alpha = list(string.ascii_uppercase)

	# list digits 
	l_digits = list(string.digits)

	# list symbols 
	l_symbols = list(string.punctuation)
	
	
	def check_valid_password(self,
						  password: str,
						  min_length :int = 12):
		"""
		Checks, if a password is valid and contains
			- uncapitalized character
			- capitalized character
			- digit
			- symbol
			- length >= min_length

		:param password: str
		:param min_length: int = 12
		:return : d_result[b_valid, l_msg: list]: dict
		"""
		l_msg = []

		# Check for empty password	
		if not password:
			print("No password given!")
			return {'b_valid': False, 'l_msg': ['Error: No password!']}

		# Escape all punctuation for safe use in regex
		sym_class = re.escape(''.join(self.l_symbols))
		# print(sym_class)

		#********************************************
		# Regex pattern explanation
		#
		# ^						Start of string
		# (?=.*[a-z]			Lookahead: at least one lowercase letter
		# (?=.*[A-Z]			Lookahead: at least one uppercase letter
		# (?=.*\d)				Lookahead: at least one digit
		# (?=.*[<symbols>])		Lookahead: at least one symbol from string.punctuations
		# [^\s}{min_length,}	Actual allowed characters (no whitespace, min_length or more)
		# $ 					End of string	
		#********************************************

		full_pattern = rf'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[{sym_class}])[^\s]{{{min_length},}}$'


		if len(password) < min_length:
#			print(f"Password length of {password} < {min_length}")
			l_msg.append(f'Error: Password must have at least {min_length} characters!')
#		else:
#			print(f"Password length of {password} >= {min_length}")
		
		if not re.search(r'[a-z]', password):
#			print(f"No uncapitalized char in {password}")
			l_msg.append('Error: No uncapitalized character in password!')
#		else:
#			print(f"Uncapitalized char found in {password}")

		if not re.search(r'[A-Z]', password):
#			print(f"No capitalized char in {password}")
			l_msg.append('Error: No capitalized character in password!')
#		else:
#			print(f"Capitalized char found in {password}")

		if not re.search(r'\d', password):
#			print(f"No digit in {password}")
			l_msg.append('Error: No digit character in password!')
#		else:
#			print(f"Digit found in {password}")

		if not re.search(rf'[{sym_class}]', password):
#			print(f"No symbol in {password}")
			l_msg.append('Error: No symbol character in password!')
#		else:
#			print(f"Symbol found in {password}")

		if re.search(r'\s', password):
#			print(f"{password} contains whitespace.")
			l_msg.append(f'Error: Password must not contain whitespace!')
#		else:
#			print(f"{password} contains no whitespace.")

		return {'b_valid': len(l_msg) == 0, 'l_msg': l_msg}


	def create_secure_password(self, length: int = 25) -> str:
		"""
		Creates a secure password with a given length, but at least with 12 characters.
		:param length: int = 25
		:return pw: str
		"""
		# instantiate variables
		pw = ''
		l_pw_raw = []
		d_group = {
				'0': self.l_alpha,
				'1': self.l_cap_alpha,
				'2': self.l_digits,
				'3': self.l_symbols
				}

		# minimal length of passwords are 12 characters
		if length < 12:
			length = 12

		# get one character from each group first and append to the list
		l_pw_raw.append(random.choice(self.l_alpha))
		l_pw_raw.append(random.choice(self.l_cap_alpha))
		l_pw_raw.append(random.choice(self.l_digits))
		l_pw_raw.append(random.choice(self.l_symbols))

		# fill list up wih characters from randomized groups
		for i in range(length-4):
			i_rand = random.randrange(0,4)
			rand_char = random.choice(d_group[str(i_rand)])
			l_pw_raw.append(rand_char)

		# shuffle the list and create pw-string to return
		random.shuffle(l_pw_raw)
		for c in l_pw_raw:
			pw += c
		return pw


	def check_valid_email(self, email: str):
		"""
		Checks, if email address is valid.
		:param email: str
		:return d_valid_email: dict {'b_valid': bool, 'l_msg': []}
		"""
		# initialize variables
		b_valid = False
		l_msg = []

		# check if email is given
		if not email:
			l_msg.append('Error: No email!')
			return {'b_valid': False, 'l_msg': l_msg}

		# step 0: lowercase
		email = email.strip().lower()

		# step 1: define regex pattern for email validation
		# Explanation:
		# ^ 					--> start of string
		# [a-z0-9._%+-]{2,}		--> start of string
		# @ 					--> start of string
		# [a-z0-9.-]{2,}		--> start of string
		# \. 					--> start of string
		# [a-z]{2,}				--> start of string
		# $ 					--> start of string
		email_pattern = r'^[a-z0-9._%+-]{2,}@[a-z0-9.-]{2,}\.[a-z]{2,}$'
		
		# step 2: check match
		if re.match(email_pattern, email):
			b_valid = True
		else:
			# if invalid, find reason for better feedback
			if '@' not in email:
				l_msg.append('Error: Email address contains no @!')
			else:
				parts = email.split('@')
				if len(parts[0]) < 2:
					l_msg.append('Error: Part before @ contains less than 2 characters!')
				if '.' not in email:
					l_msg.append('Error: Email address contains no dot!')
				else:
					domain_parts = parts[1].split('.')
					if len(domain_parts[0]) < 2:
						l_msg.append('Error: Email part between @ and dot must contain at least 2 characters!')
					if len(domain_parts[-1]) < 2:
						l_msg.append('Error: Email oart behind @ and dot must contain at least 2 characters!')
		return {'b_valid': b_valid, 'l_msg': l_msg}
	


	def make_salt(self, length: int = 16) -> str:
		"""
		Creates salt for password hash.
		:param length: int = 16
		:return : str
		"""
		salt = os.urandom(length)
		return base64.b64encode(salt).decode('utf-8') 


	def generate_hashed_password(self,
							  password: str,
							  my_salt: str) -> str:
		"""
		Generates a SHA-256 hash of the	password combined with the salt.
		:param password: str
		:param mysalt: str
		:return hashed_password: str
		"""
		salted_password = (my_salt + password).encode('utf-8')
		hashed_password = hashlib.sha256(salted_password).hexdigest() 
		return hashed_password


	def check_hashed_password(self, 
						   login_password: str, 
						   db_password: str, 
						   db_salt: str,
						   db_pepper: str) -> bool:
		"""
		Verifies if the provided password matches the stored hash.
		:param login_password: str
		:db_password: str
		:db_salt: str
		:db_pepper: str
		:return : bool
		"""
		hashed_login_password_salted = self.generate_hashed_password(login_password, db_salt)
		hashed_login_password_peppered = self.generate_hashed_password(hashed_login_password_salted, db_pepper)
		return hashed_login_password_peppered == db_password
#=== main


if __name__ == '__main__':
	creds = Creds()
	password = 'Password!0815@4711'
	salt = creds.make_salt()
	hashed_password = creds.generate_hashed_password(password, salt)
	checked_password = creds.check_hashed_password(password, hashed_password, salt)
	
	print(f'Password: {password}')
	print(f'Salt: {salt}')
	print(f'Hashed password: {hashed_password}')
	print(f'Checked: {checked_password}')