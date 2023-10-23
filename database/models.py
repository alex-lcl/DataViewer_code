from .db import db
from flask_bcrypt import generate_password_hash, check_password_hash


class User(db.Document):
	""" Classe permettant la création et gestion des utilisateurs """

	# Attributs nécessaires à la création d'un compte utilisateur
	email = db.EmailField(required=True, unique=True)
	password = db.StringField(required=True, min_length=6)		# mot de passe de minimum 6 caractères
	
	def hash_password(self):
		""" Permet de transformer le mot de passe (qui est une simple String) en hash """
		self.password = generate_password_hash(self.password).decode('utf8')
	
	def check_password(self, password):
		""" Permet de vérifier que le mot de passe utilisé par l'utilisateur lors de sa connexion
		 		produit un hash égal à celui sauvegardé dans la base de données
		 		(en d'autres mots, vérifier que le mot de passe pour l'inscription et la connexion sont les mêmes)
		"""
		return check_password_hash(self.password, password)
