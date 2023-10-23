from flask import request, Response
from flask_jwt_extended import create_access_token
from database.models import User
from flask_restful import Resource
from mongoengine.errors import FieldDoesNotExist, NotUniqueError, DoesNotExist
from resources.errors import SchemaValidationError, EmailAlreadyExistsError, UnauthorizedError, InternalServerError
import datetime


class SignupApi(Resource):
	""" Classe permettant l'inscription d'un utilisateur """

	def post(self):
		try:
			# Récupération des informations de l'utilisateur
			body = request.get_json()
			# Création d'un utilisateur
			user = User(**body)
			# Encryptage de son mot de passe
			user.hash_password()
			# Sauvegarde de l'utilisateur & Récupération de son identifiant dans la base de données
			user.save()
			id = user.id
			return {'id': str(id)}, 200
		except FieldDoesNotExist:
			raise SchemaValidationError
		except NotUniqueError:
			raise EmailAlreadyExistsError
		except Exception as e:
			raise InternalServerError
		
		
class LoginApi(Resource):
	""" Classe permettant la connexion d'un utilisateur """

	def post(self):
		try:
			# Récupération des informations de l'utilisateur
			body = request.get_json()
			# Récupérer dans la base de données l'utilisateur utilisant l'adresse mail renseignée
			user = User.objects.get(email=body.get('email'))
			# Vérifier que le mot de passe saisi est bien le même que celui utilisé lors de l'inscription
			authorized = user.check_password(body.get('password'))
			if not authorized:
				raise UnauthorizedError
			# Création d'un token (clé de connexion)
			expires = datetime.timedelta(days=2)		# Valable 2 jours
			access_token = create_access_token(identity=str(user.id), expires_delta=expires)
			return {'token': access_token}, 200
		except (UnauthorizedError, DoesNotExist):
			raise UnauthorizedError
		except Exception as e:
			raise InternalServerError
