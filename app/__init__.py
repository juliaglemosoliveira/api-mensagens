from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.handlers.error_handlers import register_error_handlers_global
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
ma = Marshmallow()

def create_app():

    app = Flask(__name__)
    app.config.from_object('config.config')
    app.json.sort_keys = False
    
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    ma.init_app(app)

    register_error_handlers_global(app)

    from app.models.mensagens import Mensagem
    from app.models.usuarios import Usuario
    from app.models.comentarios import Comentario
    from app.controllers.mensagens import msg_bp
    from app.controllers.usuarios import user_bp
    from app.controllers.auth import auth_bp

    app.register_blueprint(msg_bp, url_prefix='/mensagens')
    app.register_blueprint(user_bp, url_prefix='/usuarios')
    app.register_blueprint(auth_bp, url_prefix='/auth')

    return app