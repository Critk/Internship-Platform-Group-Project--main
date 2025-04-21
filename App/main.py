import os
from flask import Flask, render_template
from flask_uploads import DOCUMENTS, IMAGES, TEXT, UploadSet, configure_uploads
from flask_cors import CORS
from werkzeug.utils import secure_filename
from werkzeug.datastructures import  FileStorage
from flask_login import LoginManager
from App.controllers import get_user
from App.database import db

from App.database import init_db
from App.config import load_config


from App.controllers import (
    setup_jwt,
    add_auth_context
)

from App.views import views, setup_admin


login_manager = LoginManager()

def load_user(user_id):
    return get_user(user_id)



def add_views(app):
    for view in views:
        app.register_blueprint(view)

def create_app(overrides={}):
    app = Flask(__name__, static_url_path='/static')
    load_config(app, overrides)
    
    CORS(app)
    add_auth_context(app)
    photos = UploadSet('photos', TEXT + DOCUMENTS + IMAGES)
    configure_uploads(app, photos)
    add_views(app)
    init_db(app)
    with app.app_context():
        db.create_all()
    jwt = setup_jwt(app)
    setup_admin(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth_views.login_action'  # or your actual login route
    login_manager.user_loader(load_user)  # THIS is the missing piece


    @jwt.invalid_token_loader
    @jwt.unauthorized_loader
    def custom_unauthorized_response(error):
        return render_template('401.html', error=error), 401
    app.app_context().push()
    return app 