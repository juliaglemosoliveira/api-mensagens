from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():

    app = Flask(__name__)
    app.config.from_object('config.config')
    

    db.init_app(app)
    migrate.init_app(app, db)

    from app.models.mensagens import Mensagem
    from app.models.usuarios import Usuario
    from app.models.comentarios import Comentario
    from app.controllers.mensagens import msg_bp
    from app.controllers.usuarios import user_bp
    from app.controllers.comentarios import cmt_bp
    app.register_blueprint(msg_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(cmt_bp)

    #with app.app_context():
    #    db.create_all()

    return app