import os
import json

import connexion
from connexion.resolver import MethodViewResolver
from dotenv import load_dotenv
from flask import Response
from flask_login import LoginManager
from flask_pymongo import ObjectId
from marshmallow.exceptions import ValidationError


load_dotenv()


def create_app(env):
    from db import mongo

    connex_app = connexion.FlaskApp(
        __name__,
        specification_dir='openapi/',
        resolver=MethodViewResolver('api')
    )
    connex_app.add_api('openapi.yaml')

    if env:
        connex_app.app.config['FLASK_ENV'] = env

    # Load secret_key from .env
    connex_app.app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

    # Load default settings
    connex_app.app.config.from_object('config.BaseConfig')

    # Load specific settings depending on environment
    if env == 'testing':
        connex_app.app.config.from_object('config.TestingConfig')

    if env == 'development':
        from flask_debugtoolbar import DebugToolbarExtension
        DebugToolbarExtension(connex_app.app)

    # Initializing mongo
    mongo.init_app(connex_app.app)

    # Adding validation error handler
    def handle_validation_error(e):
        return Response(json.dumps(e.messages), 400, mimetype='application/json')
    connex_app.app.register_error_handler(ValidationError, handle_validation_error)

    # Initializing flask_login
    login_manager = LoginManager()
    login_manager.init_app(connex_app.app)
    login_manager.login_view = 'auth.login'
    # connex_app.app.login_manager = login_manager

    @login_manager.user_loader
    def load_user(user_id):
        from models import User
        return User(**mongo.db.users.find_one({'_id': ObjectId(user_id)}))

    # Adding auth views
    from views import auth
    connex_app.app.register_blueprint(auth.bp)

    # Adding custom management commands
    from commands import (
        create_indexes, generate_users, generate_transaction_for_user
    )
    connex_app.app.cli.add_command(create_indexes)
    connex_app.app.cli.add_command(generate_users)
    connex_app.app.cli.add_command(generate_transaction_for_user)

    return connex_app.app


env = os.environ.get('FLASK_ENV', 'development')
app = create_app(env)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

