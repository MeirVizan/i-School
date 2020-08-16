from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from iSchoolApp.config import Config


# database in flask using SQLAlchemy
db = SQLAlchemy()
# for a password (hash function)
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'teacher.login'
login_manager.login_view = 'admin.loginAdminister'
# get info about the login
login_manager.login_message_category = 'info'


def create_app(config_class=Config):
    # for app server of flask
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # getting access to routes by using Blueprint
    from iSchoolApp.main_page.routes import main_page
    from iSchoolApp.teacher.routes import teacher
    from iSchoolApp.admin.routes import admin
    from iSchoolApp.errors.handlers import errors

    app.register_blueprint(main_page)
    app.register_blueprint(teacher)
    app.register_blueprint(admin)
    app.register_blueprint(errors)

    return app


