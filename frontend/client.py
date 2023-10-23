from flask import Flask, render_template, request
import requests, json

#URL_backend = "http://dataviewer.api.localhost:8000/apidocs/"
URL_backend = "http://dataviewer.api.localhost:5000/"

app = Flask(__name__)

@app.route('/')
def index():
   return render_template('index.html')


@app.route('/formulaire',methods = ['POST', 'GET', 'DELETE', 'PUT'])
def formulaire():
    if request.method == 'POST':
        formulaire = request.form # réccupération des données du formulaire
        token = formulaire['token'] # réccupération du token d'identification 'token'
        """ Le formulaire pour POST doit être de cette forme:
            {   "token": "", 
                "classe_age": "",
                "commune_residence": "",
                "date": "", #date, string
                "date_reference": "", #date, string
                "effectif_cumu_1_inj": 0, #float
                "effectif_cumu_termine": 0, #float
                "libelle_classe_age": "",
                "libelle_commune": "",
                "population_carto": 0, #float
                "semaine_injection": "",
                "taux_1_inj": 0, #float
                "taux_cumu_1_inj": 0, #float
                "taux_cumu_termine": 0, #float
                "taux_termine": 0}#float"""
         # on fait la requête sur le backend
        r = requests.post(URL_backend+'vaccination/',headers={'Authorization': 'TOK:'+token}, json=formulaire)
        data = json.loads(r.text) # le json renvoyé devient un dictionnaire
        return render_template("result.html",result = data)
    
    elif request.method == 'PUT':
        formulaire = request.form # réccupération des données du formulaire
        id = formulaire['recordid'] # réccupération de l'identifiant de l'entrée à supprimer
        token = formulaire['token'] # réccupération du token d'identification 'token'
        """ Le formulaire pour POST doit être de cette forme:
            {   "token": "",
                "classe_age": "",
                "commune_residence": "",
                "date": "",
                "date_reference": "",
                "effectif_cumu_1_inj": 0,
                "effectif_cumu_termine": 0,
                "libelle_classe_age": "",
                "libelle_commune": "",
                "population_carto": 0,
                "semaine_injection": "",
                "taux_1_inj": 0,
                "taux_cumu_1_inj": 0,
                "taux_cumu_termine": 0,
                "taux_termine": 0}"""
        # récupération des modifications
        modifications = {}
        for key, value in formulaire.items():
            if value != "" or value != 0:
                modifications[key] = value
        # on fait la requête sur le backend
        r = requests.put(URL_backend+'vaccination/'+id,headers={'Authorization': 'TOK:'+token}, json=formulaire)
        # récupération des données du backend
        data = json.loads(r.text)#le json renvoyé devient un dictionnaire
        return render_template("result.html",result = modifications)
    
    elif request.method == 'DELETE':
        id = request.form['recordid'] # réccupération de l'identifiant de l'entrée à supprimer
        token = request.form['token'] # réccupération du token d'identification 'token'
        """ Le formulaire pour POST doit être de cette forme:
            {   "token": "" 
                "recordid": "" }"""
        # on fait la requête sur le backend
        r = requests.post(URL_backend+'vaccination/'+id,headers={'Authorization': 'TOK:'+token})
        # récupération des données du backend
        data = json.loads(r.text) # le json renvoyé devient un dictionnaire
        return render_template("result.html",result = data)
    
    elif request.method == 'GET':
        formulaire = request.form # réccupération des données du formulaire
        token = formulaire['token'] # réccupération du token d'identification 'token'
        """ Le formulaire pour POST doit être de cette forme:
            {   "token": "" 
            ### champs facultatifs, mais si présent: soit commune, soit commune + semaine, soit commune + semaine + age ###
                "commune_residence": "",
                "semaine_injection": ""
                "classe_age": "", }
            ou de cette forme:    
                {   "token": "" 
                    "recordid": ""}"""
        
        if "recordid" in formulaire.keys():
            id = formulaire["recordid"]
            r = requests.get(URL_backend+'vaccination/'+id,headers={'Authorization': 'TOK:'+token}, json=formulaire)
        
        elif formulaire["commune_residence"] != "" and formulaire["semaine_injection"] != "" and formulaire["classe_age"] != "":
            code_commune = formulaire["commune_residence"]
            semaine = formulaire["semaine_injection"]
            age = formulaire["classe_age"]
            r = requests.get(URL_backend+'vaccination/commune/'+code_commune+"/semaine/"+semaine+"/classe_age/"+age,headers={'Authorization': 'TOK:'+token}, json=formulaire)
        
        elif formulaire["commune_residence"] != "" and formulaire["semaine_injection"] == "" and formulaire["classe_age"] == "":
            code_commune = formulaire["commune_residence"]
            semaine = formulaire["semaine_injection"]
            r = requests.get(URL_backend+'vaccination/commune/'+code_commune+"/semaine/"+semaine,headers={'Authorization': 'TOK:'+token}, json=formulaire)
        
        elif formulaire["commune_residence"] == "" and formulaire["semaine_injection"] == "" and formulaire["classe_age"] == "":
            code_commune = formulaire["commune_residence"]
            r = requests.get(URL_backend+'vaccination/commune/'+code_commune,headers={'Authorization': 'TOK:'+token}, json=formulaire)
        
        # récupération des données du backend
        data = json.loads(r.text) # le json renvoyé devient un dictionnaire
        return render_template("result.html",result = data)



if __name__ == 'main':
   app.run(debug = True)