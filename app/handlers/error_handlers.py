from flask import jsonify
from werkzeug.exceptions import NotFound, BadRequest

def register_error_handlers_global(app):
    @app.errorhandler(NotFound)
    def error_not_found(e):
        return jsonify({'Mensagem': 'Recurso nao encontrado'}), 404

def register_error_handlers_msg(msg_bp):
    @msg_bp.errorhandler(BadRequest)
    def error_bad_request(e):
        descricao = getattr(e, 'description', None)

        erros_json = [
            "Failed to decode JSON object",
            "Expecting value",
            "Expecting ',' delimiter",
            "Expecting property name enclosed in double quotes",
            "Unterminated string starting at"]

        if descricao and descricao != BadRequest.description and not any(error in descricao for error in erros_json):
            return jsonify({'Mensagem': descricao}), 400
        
        return jsonify({'Mensagem': 'Requisição mal formada, por favor, envie em um formato JSON adequado.'}), 400
    
    