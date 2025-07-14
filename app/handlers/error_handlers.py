from flask import jsonify
from werkzeug.exceptions import NotFound, BadRequest

def register_error_handlers_global(app):
    @app.errorhandler(NotFound)
    def error_not_found(e):
        return jsonify({'Mensagem': 'Recurso nao encontrado'}), 404

def register_error_handlers_msg(msg_bp):
    @msg_bp.errorhandler(BadRequest)
    def error_bad_request(e):
        return jsonify({'Mensagem': 'Requisição mal formada, por favor, envie em um formato JSON adequado.'}), 400

    
    