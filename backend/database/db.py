from flask_mongoengine import MongoEngine

db = MongoEngine()

def initialize_db(app):
    """ Initialisation d'une base de donnée MongoDB liée à l'application web """
    db.init_app(app)
    
