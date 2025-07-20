from flask import jsonify
from werkzeug.exceptions import NotFound, BadRequest, Conflict, Unauthorized, Forbidden

def register_error_handlers_global(app):

    @app.errorhandler(BadRequest)
    def error_bad_request(e):
        descricao = getattr(e, 'description', None)

        if isinstance(descricao, str) and 'Failed to decode JSON object' in descricao:
            return jsonify({'Mensagem': 'Requisição mal formada, por favor, envie em um formato JSON adequado.'}), 400

        if descricao and descricao != BadRequest.description:
            return jsonify({'Mensagem': descricao}), 400
        
        return jsonify({'Mensagem': 'Requisição mal formada, por favor, envie em um formato JSON adequado.'}), 400
    
    @app.errorhandler(Unauthorized)
    def error_handler_unauthorized(e):
        descricao = getattr(e, 'description', None)
        if descricao and descricao != Unauthorized.description:
            return jsonify({'Mensagem': descricao}), 401
        return jsonify({'Mensagem': 'Você não tem autorização para acessar esse recurso.'}), 401
    
    @app.errorhandler(Forbidden)
    def error_handler_unauthorized(e):
        descricao = getattr(e, 'description', None)
        if descricao and descricao != Forbidden.description:
            return jsonify({'Mensagem': descricao}), 403
        return jsonify({'Mensagem': 'Você não tem autorização para executar essa ação.'}), 403

    @app.errorhandler(NotFound)
    def error_not_found(e):
        return jsonify({'Mensagem': 'Recurso nao encontrado'}), 404

    @app.errorhandler(Conflict)
    def error_handler_conflict(e):
        descricao = getattr(e, 'description', None)
        if descricao and descricao != Conflict.description:
            return jsonify({'Mensagem': descricao}), 409
        return jsonify({'Mensagem': 'Conflito de dados.'}), 409
    
    