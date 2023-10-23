import json
import datetime
from flask import Flask, request, jsonify, make_response, Response
from flask_restful import Resource, Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, jwt_required
from flasgger import Swagger
from flask_apscheduler import APScheduler
import requests

from database.db import initialize_db
from database.models import User
from resources.auth import SignupApi, LoginApi
from resources.errors import errors


# set configuration values for the APSheduler
class Config:
    SCHEDULER_API_ENABLED = True


# app creation
app = Flask(__name__)
app.config.from_envvar('ENV_FILE_LOCATION')
app.config.from_object(Config())
api = Api(app, errors=errors)

# utils related to the app
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
swagger = Swagger(app)

# initialize scheduler
scheduler = APScheduler()


date = datetime.datetime.strptime("2022-09", '%Y-%W')
with open("donnees-de-vaccination-par-commune.json", "r") as f:
    data = f.read()
    records = json.loads(data)


class DonneesCommune(Resource):
    
    def get(self):
        """Retourne la liste des entrées du dataset
        ---
        tags:
          - restful
        responses:
          200:
            description: Liste des entrées de la base de donnée
            schema:
              id: donnees-de-vaccination
              properties:
                datasetid:
                  type: string
                  description: Le nom de dataset
                  default: donnees-de-vaccination-par-commune
                recordid:
                  type: string
                  description: L'identifiant de l'entrée de la base de donnée
                  default: 8d40bdd24b81cc060ba7ee0388db711d4fa7eac5
                fields:
                  type: object
                  description: Les données d'une entrée
                  properties:
                    classe_age:
                      type: string
                      default: 65-74
                    libelle_commune:
                      type: string
                      default: MONTANAY
                    date_reference:
                      type: string
                      default: 2022-03-06
                    taux_cumu_1_inj:
                      type: string
                      default: 0.963
                    population_carto:
                      type: string
                      default: 380
                    date:
                      type: string
                      default: 2021-11-14
                    semaine_injection:
                      type: string
                      default: 2021-45
                    libelle_classe_age:
                      type: string
                      default: de 65 à 74 ans
                    effectif_cumu_1_inj:
                      type: string
                      default: 360
                    effectif_cumu_termine:
                      type: string
                      default: 360
                    taux_cumu_termine:
                      type: string
                      default: 0.96
                record_timestamp:
                  type: string
                  description: La date et l'heure de la dernière modification
                  default: 2022-03-11T10:30:35.173Z
        """
        global records
        return make_response(jsonify(records), 200)

    @jwt_required()
    def post(self):
        """
        Ajouter une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              id: Entry
              properties:
                datasetid:
                    type: string
                    description: Le nom de dataset
                    default: donnees-de-vaccination-par-commune
                recordid:
                    type: string
                    description: L'identifiant de l'entrée de la base de donnée
                    default: 8d40bdd24b81cc060ba7ee0388db711d4fa7eac5
                classe_age:
                    type: string
                    default: 65-74
                libelle_commune:
                    type: string
                    default: MONTANAY
                date_reference:
                    type: string
                    default: 2022-03-06
                taux_cumu_1_inj:
                    type: string
                    default: 0.963
                population_carto:
                    type: string
                    default: 380
                date:
                    type: string
                    default: 2021-11-14
                semaine_injection:
                    type: string
                    default: 2021-45
                libelle_classe_age:
                    type: string
                    default: de 65 à 74 ans
                effectif_cumu_1_inj:
                    type: string
                    default: 360
                effectif_cumu_termine:
                    type: string
                    default: 360
                taux_cumu_termine:
                    type: string
                    default: 0.96
        responses:
          201:
            description: L'entrée a été crée
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          400:
            description: Pas de clef 'recordid' ou 'une 'recordid' déjà utilisé dans la nouvelle entrée
        """
        new_datas = request.json
        if "recordid" not in new_datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 400)
        rec = {'datasetid':"donnees-de-vaccination-par-commune", "fields":{}}
        for data in new_datas.keys():
            if data == "recordid":
                rec["recordid"] = new_datas["recordid"]
            elif data == "classe_age":
                rec["fields"]["classe_age"] = new_datas["classe_age"]
            elif data == "commune_residence":
                rec["fields"]["commune_residence"] = new_datas["commune_residence"]
            elif data == "date":
                rec["fields"]["date"] = new_datas["date"]
            elif data == "date_reference":
                rec["fields"]["date_reference"] = new_datas["date_reference"]
            elif data == "effectif_cumu_1_inj":
                rec["fields"]["effectif_cumu_1_inj"] = new_datas["effectif_cumu_1_inj"]
            elif data == "libelle_classe_age":
                rec["fields"]["libelle_classe_age"] = new_datas["libelle_classe_age"]
            elif data == "libelle_commune":
                rec["fields"]["libelle_commune"] = new_datas["libelle_commune"]
            elif data == "population_carto":
                rec["fields"]["population_carto"] = new_datas["population_carto"]
            elif data == "semaine_injection":
                rec["fields"]["semaine_injection"] = new_datas["semaine_injection"]
            elif data == "taux_cumu_1_inj":
                rec["fields"]["taux_cumu_1_inj"] = new_datas["taux_cumu_1_inj"]
            elif data == "taux_cumu_termine":
                rec["fields"]["taux_cumu_termine"] = new_datas["taux_cumu_termine"]
            rec["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
        global records
        for r in records:
            if rec["recordid"] == r["recordid"]:
                return make_response(jsonify({"message": "already used recordid"}), 400)
        records.append(rec)
        return make_response(jsonify(rec), 201)


class DonneeCommune(Resource):

    def get(self, id):
        """
        Lire une entrée
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: id
            required: true
            description: L'identifiant de l'entrée (recordid)
            type: string
        responses:
          200:
            description: Les données de  l'entrée
            schema:
              $ref: '#/definitions/donnees-de-vacination'
        """
        global records
        for record in records:
            if record["recordid"] == id:
                return make_response(jsonify(record), 200 )
        return make_response(jsonify({"message": "data not found"}), 204)

    @jwt_required()
    def put(self, id):
        """
        Modifier une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Entry'
          - in: path
            name: id
            required: true
            description: L'identifiant de l'entrée (recordid)
            type: string
        responses:
          201:
            description: L'entrée a été modifié
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          204:
            description: 'recordid' n'a pas été trouvé dans les données d'entrées
          404:
            description: L'entrée à modifier n'a pas été trouvé
        """
        global records
        datas = request.json
        if "recordid" not in datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 204)
        for record in records:
            if record["recordid"] == datas["recordid"]:
                for data in datas.keys():
                    if data == "classe_age":
                        record["fields"]["classe_age"] = datas["classe_age"]
                    elif data == "commune_residence":
                        record["fields"]["commune_residence"] = datas["commune_residence"]
                    elif data == "date":
                        record["fields"]["date"] = datas["date"]
                    elif data == "date_reference":
                        record["fields"]["date_reference"] = datas["date_reference"]
                    elif data == "effectif_cumu_1_inj":
                        record["fields"]["effectif_cumu_1_inj"] = datas["effectif_cumu_1_inj"]
                    elif data == "libelle_classe_age":
                        record["fields"]["libelle_classe_age"] = datas["libelle_classe_age"]
                    elif data == "libelle_commune":
                        record["fields"]["libelle_commune"] = datas["libelle_commune"]
                    elif data == "population_carto":
                        record["fields"]["population_carto"] = datas["population_carto"]
                    elif data == "semaine_injection":
                        record["fields"]["semaine_injection"] = datas["semaine_injection"]
                    elif data == "taux_cumu_1_inj":
                        record["fields"]["taux_cumu_1_inj"] = datas["taux_cumu_1_inj"]
                    elif data == "taux_cumu_termine":
                        record["fields"]["taux_cumu_termine"] = datas["taux_cumu_termine"]
                record["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
                record_modifie = record
                return make_response(jsonify(record_modifie), 201)
        return make_response(jsonify({"message": "data not found"}), 404)

    @jwt_required()
    def delete(self, id):
        """
        Supprimer une entrée
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: id
            required: true
            description: L'identifiant de l'entrée (recordid)
            type: string
        responses:
          200: 
            description: L'entrée a été supprimée
          204:
            description: L'entrée voulu n'a pas été trouvé
        """
        global records
        find = False
        new_records = []
        for record in records:
            if record["recordid"] == id:
                find = True
                continue
            new_records.append(record)
        records = new_records
        if find == True:
            return make_response(jsonify({"valdation": "data deleted"}), 200)
        else:
            return make_response(jsonify({"message": "data not found"}), 204)


class Commune(Resource):

    def get(self):
      """Retourne la liste des codes des communes
        ---
        tags:
          - restful
        parameters:
        responses:
          200:
            description: Liste des codes des communes (commune_code)
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
      """
      global records
      communes = {"commune_code":[]}
      for record in records:
          if record["fields"]["commune_residence"] not in communes["commune_code"]:
              communes["commune_code"].append(record["fields"]["commune_residence"])
      return make_response(jsonify(communes), 200)
    

class CodeCommune(Resource):

    def get(self, code_commune):
        """Retourne la liste des entrées du dataset suivant sa commune
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: commune_code
            required: true
            description: Le code de la commune (commune_residence)
            type: string
        responses:
          200:
            description: Liste des entrées de la base de donnée suivant le libellé de commune
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
        """
        global records
        sort_records = []
        for record in records:
            if str(code_commune) == record["fields"]["commune_residence"]:
                sort_records.append(record)
        if sort_records == {}:
            return make_response(jsonify({"message": "No data"}), 200)
        return make_response(jsonify(sort_records), 200)

    @jwt_required()
    def post(self, code_commune):
        """
        Ajouter une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Entry'
          - in: path
            name: commune_code
            required: true
            description: Le code de la commune (commune_residence)
            type: string
        responses:
          201:
            description: L'entrée a été crée
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          400:
            description: La nouvelle entrée n'a pas pu être crée
        """
        new_datas = request.json
        rec = {'datasetid':"donnees-de-vaccination-par-commune", "fields":{}}
        if "recordid" not in new_datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 400)
        if "commune_residence" in new_datas.keys() and new_datas["commune_residence"] != code_commune:
            return make_response(jsonify({"message": "your entry's code_commune and the dataset one doesn't match "}), 400)
        if "commune_residence" not in new_datas.keys():
            rec["fields"]["commune_residence"] = code_commune
        for data in new_datas.keys():
            if data == "recordid":
                rec["recordid"] = new_datas["recordid"]
            elif data == "classe_age":
                rec["fields"]["classe_age"] = new_datas["classe_age"]
            elif data == "commune_residence":
                rec["fields"]["commune_residence"] = new_datas["commune_residence"]
            elif data == "date":
                rec["fields"]["date"] = new_datas["date"]
            elif data == "date_reference":
                rec["fields"]["date_reference"] = new_datas["date_reference"]
            elif data == "effectif_cumu_1_inj":
                rec["fields"]["effectif_cumu_1_inj"] = new_datas["effectif_cumu_1_inj"]
            elif data == "libelle_classe_age":
                rec["fields"]["libelle_classe_age"] = new_datas["libelle_classe_age"]
            elif data == "libelle_commune":
                rec["fields"]["libelle_commune"] = new_datas["libelle_commune"]
            elif data == "population_carto":
                rec["fields"]["population_carto"] = new_datas["population_carto"]
            elif data == "semaine_injection":
                rec["fields"]["semaine_injection"] = new_datas["semaine_injection"]
            elif data == "taux_cumu_1_inj":
                rec["fields"]["taux_cumu_1_inj"] = new_datas["taux_cumu_1_inj"]
            elif data == "taux_cumu_termine":
                rec["fields"]["taux_cumu_termine"] = new_datas["taux_cumu_termine"]
            rec["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
        global records
        for r in records:
            if rec["recordid"] == r["recordid"]:
                return make_response(jsonify({"message": "already used recordid"}), 400)
        records.append(rec)
        return make_response(jsonify(rec), 201)

    @jwt_required()
    def put(self, code_commune):
        """
        Modifier une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Entry'
          - in: path
            name: commune_code
            required: true
            description: Le code de la commune (commune_residence)
            type: string
        responses:
          201:
            description: L'entrée a été modifié
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          204:
            description: 'recordid' n'a pas été trouvé dans les données d'entrées
          404:
            description: L'entrée à modifier n'a pas été trouvé
        """
        global records
        datas = request.json
        if "recordid" not in datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 204)
        for record in records:
            if record["recordid"] == datas["recordid"]:
                for data in datas.keys():
                    if data == "classe_age":
                        record["fields"]["classe_age"] = datas["classe_age"]
                    elif data == "commune_residence":
                        record["fields"]["commune_residence"] = datas["commune_residence"]
                    elif data == "date":
                        record["fields"]["date"] = datas["date"]
                    elif data == "date_reference":
                        record["fields"]["date_reference"] = datas["date_reference"]
                    elif data == "effectif_cumu_1_inj":
                        record["fields"]["effectif_cumu_1_inj"] = datas["effectif_cumu_1_inj"]
                    elif data == "libelle_classe_age":
                        record["fields"]["libelle_classe_age"] = datas["libelle_classe_age"]
                    elif data == "libelle_commune":
                        record["fields"]["libelle_commune"] = datas["libelle_commune"]
                    elif data == "population_carto":
                        record["fields"]["population_carto"] = datas["population_carto"]
                    elif data == "semaine_injection":
                        record["fields"]["semaine_injection"] = datas["semaine_injection"]
                    elif data == "taux_cumu_1_inj":
                        record["fields"]["taux_cumu_1_inj"] = datas["taux_cumu_1_inj"]
                    elif data == "taux_cumu_termine":
                        record["fields"]["taux_cumu_termine"] = datas["taux_cumu_termine"]
                record["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
                record_modifie = record
                return make_response(jsonify(record_modifie), 201)
        return make_response(jsonify({"message": "data not found"}), 404)


class SemaineListe(Resource):

    def get(self,code_commune):
        """Retourne la liste des classes d'age
        ---
        tags:
          - restful
        parameters:
        responses:
          200:
            description: Liste des semaines d'injections (semaine_injection)
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
        """
        global records
        semaine_liste = {"semaine_injection":[]}
        for record in records:
          if record["fields"]["semaine_injection"] not in semaine_liste["semaine_injection"]:
              semaine_liste["semaine_injection"].append(record["fields"]["semaine_injection"])
        return make_response(jsonify(semaine_liste), 200)


class Semaine(Resource):

    def get(self, code_commune, semaine):
        """Retourne la liste des entrées du dataset suivant sa commune et la semaine d'injection
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: code_commune
            required: true
            description: le code de la commune(commune_residence)
            type: string
          - in: path
            name: semaine
            required: true
            description: la semaine d'injection (semaine_injection)
            type: string
        responses:
          200:
            description: Liste des entrées de la base de donnée suivant la  semaine d'injection
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
        """
        global records
        sort_records = []
        for record in records:
            if str(code_commune) == record["fields"]["commune_residence"] and str(semaine) == record["fields"]["semaine_injection"]:
                sort_records.append(record)
        if sort_records == {}:
            return make_response(jsonify({"message": "No data"}), 200)
        return make_response(jsonify(sort_records), 200)

    @jwt_required()
    def post(self, code_commune, semaine):
        """
        Ajouter une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Entry'
          - in: path
            name: code_commune
            required: true
            description: le code de la commune (commune_residence)
            type: string
          - in: path
            name: semaine
            required: true
            description: la semaine d'injection (semaine_injection)
            type: string
        responses:
          201:
            description: L'entrée a été crée
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          400:
            description: La nouvelle entrée n'a pas pu être crée
        """
        new_datas = request.json
        rec = {'datasetid':"donnees-de-vaccination-par-commune", "fields":{}}
        if "recordid" not in new_datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 400)
        if "commune_residence" in new_datas.keys() and new_datas["commune_residence"] != code_commune:
            return make_response(jsonify({"message": "your entry's code_commune and the dataset one doesn't match "}), 400)
        if "semaine_injection" in new_datas.keys() and new_datas["semaine_injection"] != semaine:
            return make_response(jsonify({"message": "your entry's code_commune and the dataset one doesn't match "}), 400)
        if "commune_residence" not in new_datas.keys():
            rec["fields"]["commune_residence"] = code_commune
        if "semaine_injection" not in new_datas.keys():
            rec["fields"]["semaine_injection"] = semaine
        for data in new_datas.keys():
            if data == "recordid":
                rec["recordid"] = new_datas["recordid"]
            elif data == "classe_age":
                rec["fields"]["classe_age"] = new_datas["classe_age"]
            elif data == "commune_residence":
                rec["fields"]["commune_residence"] = new_datas["commune_residence"]
            elif data == "date":
                rec["fields"]["date"] = new_datas["date"]
            elif data == "date_reference":
                rec["fields"]["date_reference"] = new_datas["date_reference"]
            elif data == "effectif_cumu_1_inj":
                rec["fields"]["effectif_cumu_1_inj"] = new_datas["effectif_cumu_1_inj"]
            elif data == "libelle_classe_age":
                rec["fields"]["libelle_classe_age"] = new_datas["libelle_classe_age"]
            elif data == "libelle_commune":
                rec["fields"]["libelle_commune"] = new_datas["libelle_commune"]
            elif data == "population_carto":
                rec["fields"]["population_carto"] = new_datas["population_carto"]
            elif data == "semaine_injection":
                rec["fields"]["semaine_injection"] = new_datas["semaine_injection"]
            elif data == "taux_cumu_1_inj":
                rec["fields"]["taux_cumu_1_inj"] = new_datas["taux_cumu_1_inj"]
            elif data == "taux_cumu_termine":
                rec["fields"]["taux_cumu_termine"] = new_datas["taux_cumu_termine"]
            rec["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
        global records
        for r in records:
            if rec["recordid"] == r["recordid"]:
                return make_response(jsonify({"message": "already used recordid"}), 400)
        records.append(rec)
        return make_response(jsonify(rec), 201)

    @jwt_required()
    def put(self, code_commune, semaine):
        """
        Modifier une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Entry'
          - in: path
            name: code_commune
            required: true
            description: le code de la commune(commune_residence)
            type: string
          - in: path
            name: semaine
            required: true
            description: la semaine d'injection (semaine_injection)
            type: string
        responses:
          201:
            description: L'entrée a été modifié
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          204:
            description: 'recordid' n'a pas été trouvé dans les données d'entrées
          404:
            description: L'entrée à modifier n'a pas été trouvé
        """
        global records
        datas = request.json
        if "recordid" not in datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 204)
        for record in records:
            if record["recordid"] == datas["recordid"]:
                for data in datas.keys():
                    if data == "classe_age":
                        record["fields"]["classe_age"] = datas["classe_age"]
                    elif data == "commune_residence":
                        record["fields"]["commune_residence"] = datas["commune_residence"]
                    elif data == "date":
                        record["fields"]["date"] = datas["date"]
                    elif data == "date_reference":
                        record["fields"]["date_reference"] = datas["date_reference"]
                    elif data == "effectif_cumu_1_inj":
                        record["fields"]["effectif_cumu_1_inj"] = datas["effectif_cumu_1_inj"]
                    elif data == "libelle_classe_age":
                        record["fields"]["libelle_classe_age"] = datas["libelle_classe_age"]
                    elif data == "libelle_commune":
                        record["fields"]["libelle_commune"] = datas["libelle_commune"]
                    elif data == "population_carto":
                        record["fields"]["population_carto"] = datas["population_carto"]
                    elif data == "semaine_injection":
                        record["fields"]["semaine_injection"] = datas["semaine_injection"]
                    elif data == "taux_cumu_1_inj":
                        record["fields"]["taux_cumu_1_inj"] = datas["taux_cumu_1_inj"]
                    elif data == "taux_cumu_termine":
                        record["fields"]["taux_cumu_termine"] = datas["taux_cumu_termine"]
                record["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
                record_modifie = record
                return make_response(jsonify(record_modifie), 201)
        return make_response(jsonify({"message": "data not found"}), 404)


class ClasseAgeList(Resource):

    def get(self, code_commune, semaine):
        """Retourne la liste des classes d'age
        ---
        tags:
          - restful
        parameters:
        responses:
          200:
            description: Liste des classes d'age (classe_age)
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
        """
        global records
        classe_liste = {"classe_age":[]}
        for record in records:
          if record["fields"]["classe_age"] not in classe_liste["classe_age"]:
              classe_liste["classe_age"].append(record["fields"]["classe_age"])
        return make_response(jsonify(classe_liste), 200)


class ClasseAge(Resource):

    def get(self, code_commune, semaine, classe_age):
        """Retourne la liste des entrées du dataset suivant sa commune, la semaine d'injection et sa classe d'age
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: code_commune
            required: true
            description: le code de la commune(commune_residence)
            type: string
          - in: path
            name: semaine
            required: true
            description: la semaine d'injection (semaine_injection)
            type: string
          - in: path
            name: classe_age
            required: true
            description: la classe d'age s(classe_age)
            type: string
        responses:
          200:
            description: Liste des entrées de la base de donnée suivant le code de la commune, la semaine d'injection et sa classe d'age
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
        """
        global records
        sort_records = []
        for record in records:
            if str(code_commune) == record["fields"]["commune_residence"] and str(semaine) == record["fields"]["semaine_injection"] and str(classe_age) == record["fields"]["classe_age"]:
                sort_records.append(record)
        if sort_records == []:
            return make_response(jsonify({"message": "No data"}), 200)
        return make_response(jsonify(sort_records), 200)

    @jwt_required()
    def post(self, code_commune, semaine, classe_age):
        """
        Ajouter une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Entry'
          - in: path
            name: code_commune
            required: true
            description: le code de la commune(commune_residence)
            type: string
          - in: path
            name: semaine
            required: true
            description: la semaine d'injection (semaine_injection)
            type: string
          - in: path
            name: classe_age
            required: true
            description: la classe d'age (classe_age)
            type: string
        responses:
          201:
            description: L'entrée a été crée
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          400:
            description: La nouvelle entrée n'a pas pu être crée
        """
        new_datas = request.json
        rec = {'datasetid':"donnees-de-vaccination-par-commune", "fields":{}}
        if "recordid" not in new_datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 400)
        if "commune_residence" in new_datas.keys() and new_datas["commune_residence"] != code_commune:
            return make_response(jsonify({"message": "your entry's code_commune and the dataset one doesn't match "}), 400)
        if "semaine_injection" in new_datas.keys() and new_datas["semaine_injection"] != semaine:
            return make_response(jsonify({"message": "your entry's code_commune and the dataset one doesn't match "}), 400)
        if "classe_age" in new_datas.keys() and new_datas["classe_age"] != classe_age:
            return make_response(jsonify({"message": "your entry's code_commune and the dataset one doesn't match "}), 400)
        if "commune_residence" not in new_datas.keys():
            rec["fields"]["commune_residence"] = code_commune
        if "semaine_injection" not in new_datas.keys():
            rec["fields"]["semaine_injection"] = semaine
        if "classe_age" not in new_datas.keys():
            rec["fields"]["classe_age"] = classe_age
        for data in new_datas.keys():
            if data == "recordid":
                rec["recordid"] = new_datas["recordid"]
            elif data == "classe_age":
                rec["fields"]["classe_age"] = new_datas["classe_age"]
            elif data == "commune_residence":
                rec["fields"]["commune_residence"] = new_datas["commune_residence"]
            elif data == "date":
                rec["fields"]["date"] = new_datas["date"]
            elif data == "date_reference":
                rec["fields"]["date_reference"] = new_datas["date_reference"]
            elif data == "effectif_cumu_1_inj":
                rec["fields"]["effectif_cumu_1_inj"] = new_datas["effectif_cumu_1_inj"]
            elif data == "libelle_classe_age":
                rec["fields"]["libelle_classe_age"] = new_datas["libelle_classe_age"]
            elif data == "libelle_commune":
                rec["fields"]["libelle_commune"] = new_datas["libelle_commune"]
            elif data == "population_carto":
                rec["fields"]["population_carto"] = new_datas["population_carto"]
            elif data == "semaine_injection":
                rec["fields"]["semaine_injection"] = new_datas["semaine_injection"]
            elif data == "taux_cumu_1_inj":
                rec["fields"]["taux_cumu_1_inj"] = new_datas["taux_cumu_1_inj"]
            elif data == "taux_cumu_termine":
                rec["fields"]["taux_cumu_termine"] = new_datas["taux_cumu_termine"]
            rec["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
        global records
        for r in records:
            if rec["recordid"] == r["recordid"]:
                return make_response(jsonify({"message": "already used recordid"}), 400)
        records.append(rec)
        return make_response(jsonify(rec), 201)

    @jwt_required()
    def put(self, code_commune, semaine, classe_age):
        """
        Modifier une entrée
        ---
        tags:
          - restful
        parameters:
          - in: body
            name: body
            schema:
              $ref: '#/definitions/Entry'
          - in: path
            name: code_commune
            required: true
            description: le code de la commune(commune_residence)
            type: string
          - in: path
            name: semaine
            required: true
            description: la semaine d'injection (semaine_injection)
            type: string
          - in: path
            name: classe_age
            required: true
            description: la classe d'age (classe_age)
            type: string
        responses:
          201:
            description: L'entrée a été modifié
            schema:
              $ref: '#/definitions/donnees-de-vaccination'
          204:
            description: 'recordid' n'a pas été trouvé dans les données d'entrées
          404:
            description: L'entrée à modifier n'a pas été trouvé
        """
        global records
        datas = request.json
        if "recordid" not in datas.keys():
            return make_response(jsonify({"message": "not recordid in the new entry"}), 204)
        for record in records:
            if record["recordid"] == datas["recordid"]:
                for data in datas.keys():
                    if data == "classe_age":
                        record["fields"]["classe_age"] = datas["classe_age"]
                    elif data == "commune_residence":
                        record["fields"]["commune_residence"] = datas["commune_residence"]
                    elif data == "date":
                        record["fields"]["date"] = datas["date"]
                    elif data == "date_reference":
                        record["fields"]["date_reference"] = datas["date_reference"]
                    elif data == "effectif_cumu_1_inj":
                        record["fields"]["effectif_cumu_1_inj"] = datas["effectif_cumu_1_inj"]
                    elif data == "libelle_classe_age":
                        record["fields"]["libelle_classe_age"] = datas["libelle_classe_age"]
                    elif data == "libelle_commune":
                        record["fields"]["libelle_commune"] = datas["libelle_commune"]
                    elif data == "population_carto":
                        record["fields"]["population_carto"] = datas["population_carto"]
                    elif data == "semaine_injection":
                        record["fields"]["semaine_injection"] = datas["semaine_injection"]
                    elif data == "taux_cumu_1_inj":
                        record["fields"]["taux_cumu_1_inj"] = datas["taux_cumu_1_inj"]
                    elif data == "taux_cumu_termine":
                        record["fields"]["taux_cumu_termine"] = datas["taux_cumu_termine"]
                record["record_timestamp"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%F.%f")
                record_modifie = record
                return make_response(jsonify(record_modifie), 201)
        return make_response(jsonify({"message": "data not found"}), 404)


"""class Enseignant(Resource):
    def get(self):
        param = request.args
        return {'type': 'enseignants', 'param':param}
    def post(self, id_user):
        data = request.json
        return {'user_post': data, 'name': 'dddd'}
class Cours(Resource):
    def post(self, id_user):
        data = request.json
        return {'user_post': data, 'name': 'dddd'}"""


# Fonction qui se déclanche toute les 24h
@scheduler.task('interval', id='do_job_1', hours=24, misfire_grace_time=900)
def job1():
    global date, records

    # si la date actuel est supérieur à la date en mémoire
    if date < datetime.datetime.now():
        ndate=date.strftime('%Y-%W') # numéro de la semaine de l'année
        
        # et si le numéro de semaine est différent
        if ndate != datetime.datetime.now().strftime('%Y-%W'):
            # on requête pour chercher le nombre d'entrée pour la semaine
            r1 = requests.get(f'https://datavaccin-covid.ameli.fr/api/records/1.0/search/?dataset=donnees-de-vaccination-par-commune&q=&rows=10&refine.semaine_injection={ndate}')
            
            n = r1.json().get("nhits") # nombre de nouvelles entrées
            
            # on cherche l'ensemble des nouvelles entrées
            r2 = requests.get(f'https://datavaccin-covid.ameli.fr/api/records/1.0/search/?dataset=donnees-de-vaccination-par-commune&q=&rows={n}&refine.semaine_injection={ndate}')

            # on met à jour la base de donnée en mémoire
            datas = r2.json().get("records")
            for record in datas:
                records.append(record)
        
        # on met à jour la base de donnée json
        with open("donnees-de-vaccination-par-commune.json", "w") as f:
            f.write(json.dumps(records, ensure_ascii=False))
        print('Data Base updated')
    
    # on sauvegarde en mémoire la date de la dernière mis à jour
    date = datetime.datetime.now()


api.add_resource(DonneesCommune, '/api/vaccination/')
api.add_resource(DonneeCommune, '/api/vaccination/<string:id>')
api.add_resource(Commune, '/api/vaccination/commune')
api.add_resource(CodeCommune, '/api/vaccination/commune/<string:code_commune>')
api.add_resource(SemaineListe, '/api/vaccination/commune/<string:code_commune>/semaine')
api.add_resource(Semaine, '/api/vaccination/commune/<string:code_commune>/semaine/<string:semaine>')
api.add_resource(ClasseAgeList, '/api/vaccination/commune/<string:code_commune>/semaine/<string:semaine>/classe_age')
api.add_resource(ClasseAge, '/api/vaccination/commune/<string:code_commune>/semaine/<string:semaine>/classe_age/<string:classe_age>')
api.add_resource(SignupApi, '/api/auth/signup')
api.add_resource(LoginApi, '/api/auth/login')


app.config['MONGODB_SETTINGS'] = {'host': 'mongodb://localhost:27017/dataviewer_api'}
initialize_db(app)


if __name__ == '__main__':
    scheduler.start()
    port = 5000
    app.run(use_reloader=False, debug=True, host="dataviewer.api.localhost", port=port)
