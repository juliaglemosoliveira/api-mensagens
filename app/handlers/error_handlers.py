from flask import jsonify
from werkzeug.exceptions import NotFound, BadRequest

def register_error_handler(app):
    @app.errorhandler(BadRequest)
    def error_bad_request(e):
        return jsonify({'Mensagem: Requisição mal formada, deve-se enviar um JSON.'})