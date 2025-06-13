from flask import Flask


def create_app():

    app = Flask(__name__)
    app.config.from_object('config.config')

    db.init_app(app)

    from app.models.caixa_de_entrada import Entrada
    from app.controllers.routes import msg_bp
    app.register_blueprint(msg_bp)

    with app.app_context():
        db.create_all()

    return app