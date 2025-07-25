from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from app.handlers.error_handlers import register_error_handlers_global
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__)
    app.config.from_object('config.config')
    app.config['JWT_SECRET_KEY'] = 'sua_chave_secreta'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = 3600  # 1 hora
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = 604800  # 7 dias

    jwt = JWTManager(app)
    db.init_app(app)
    migrate.init_app(app, db)

    from app.models.mensagens import Mensagem
    from app.models.usuarios import Usuario
    from app.models.comentarios import Comentario
    from app.controllers.mensagens import msg_bp
    from app.controllers.usuarios import user_bp
    from app.controllers.comentarios import cmt_bp
    from app.controllers.autenticacao import auth_bp

    register_error_handlers_global(app)

    app.register_blueprint(msg_bp, url_prefix='/mensagens')
    app.register_blueprint(user_bp, url_prefix='/usuarios')
    app.register_blueprint(cmt_bp, url_prefix='/comentarios')
    app.register_blueprint(auth_bp, '/autenticar')

    
    

    #with app.app_context():
    #    db.create_all()

    return app