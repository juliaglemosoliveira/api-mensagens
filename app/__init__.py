from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():

    app = Flask(__name__)
    app.config.from_object('config.config')

    db.init_app(app)

    from app.models.mensagens import Entrada
    from app.controllers.mensagens import msg_bp
    app.register_blueprint(msg_bp)

    with app.app_context():
        db.create_all()

    return app