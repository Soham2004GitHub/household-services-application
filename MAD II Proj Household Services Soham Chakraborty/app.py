from flask import Flask
from backend.config import LocalDevelopmentConfig
from backend.models import db, User, Role
from flask_security import Security, SQLAlchemyUserDatastore, auth_required
from flask_caching import Cache
from backend.celery.celery_factory import celery_init_app
import flask_excel as excel

from flask_cors import CORS
#app = Flask(__name__)





def createApp():
    app = Flask(__name__, template_folder='frontend', static_folder='frontend', static_url_path='/static')
    #CORS(app)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5000"}})
    app.config.from_object(LocalDevelopmentConfig)
    db.init_app(app)

    datastore = SQLAlchemyUserDatastore(db, User, Role)
    
    # cache init
    cache = Cache(app)
    app.cache = cache

    app.security = Security(app, datastore=datastore, register_blueprint=False)
    app.app_context().push()

    
    return app 

app = createApp()

celery_app = celery_init_app(app)

# 

import backend.create_initial_data

import backend.routes


import backend.celery.celery_schedule

excel.init_excel(app)

if (__name__ == '__main__'):
    app.run(debug=True)

