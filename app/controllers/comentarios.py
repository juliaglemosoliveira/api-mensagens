from flask import Blueprint, request, jsonify
from app import db
from app.models.comentarios import Comentario
from app.models.mensagens import Mensagem

cmt_bp = Blueprint('cmt_bp', __name__)

@cmt_bp.route('/comentarios', methods=['POST'])
def create_comentario():
    data = request.get_json()

    comentario = data.get('comentario')
    data_hora = data.get('data_hora')  # Opcional, pode ser None
    autor = data.get('autor', 1)
    mensagem_id = data.get('mensagem_id')

    # Validação: mensagem precisa existir
    mensagem = Mensagem.query.get(mensagem_id)
    if not mensagem:
        return jsonify({'Mensagem': 'Nenhuma mensagem com esse ID, tente outro!'}), 404

    # Criação do comentário
    novo_comentario = Comentario(
        comentario=comentario,
        autor=autor,
        mensagem_id=mensagem_id
        # data_hora será preenchido automaticamente se não for enviado
    )

    db.session.add(novo_comentario)
    db.session.commit()

    return jsonify(novo_comentario.json()), 201

# READ ALL
@cmt_bp.route('/comentarios', methods=['GET'])
def get_comentarios():
    comentarios = Comentario.query.all()
    return jsonify([cmt.json() for cmt in comentarios]), 200

# READ ONE
@cmt_bp.route('/comentarios/<int:id>', methods=['GET'])
def get_comentario(id):
    comentario = Comentario.query.get(id)
    if not comentario:
        return jsonify({'Mensagem': 'Comentário não encontrado!'}), 404
    return jsonify(comentario.json()), 200

# UPDATE
@cmt_bp.route('/comentarios/<int:id>', methods=['PUT'])
def update_comentario(id):
    comentario = Comentario.query.get(id)
    if not comentario:
        return jsonify({'Mensagem': 'Comentário não encontrado!'}), 404

    data = request.get_json()

     # Bloqueia alteração de autor e mensagem_id
    if 'autor' in data or 'mensagem_id' in data:
        return jsonify({'Mensagem': 'Não é permitido alterar autor ou mensagem_id de um comentário.'}), 400

    comentario.comentario = data.get('comentario', comentario.comentario)
    db.session.commit()
    return jsonify(comentario.json()), 200

# DELETE
@cmt_bp.route('/comentarios/<int:id>', methods=['DELETE'])
def delete_comentario(id):
    comentario = Comentario.query.get(id)
    if not comentario:
        return jsonify({'Mensagem': 'Comentário não encontrado!'}), 404
    
    data = request.get_json()
    autor_id = data.get('autor')

    if not autor_id:
        return jsonify({'Mensagem': 'ID do autor é obrigatório para exclusão.'}), 400

    if comentario.autor != autor_id:
        return jsonify({'Mensagem': 'Você não tem permissão para excluir este comentário.'}), 403
    
    db.session.delete(comentario)
    db.session.commit()
    return jsonify({'Mensagem': 'Comentário deletado com sucesso!'}), 200

#Endpoint para Comentario por Mensagem
@cmt_bp.route('/mensagens/<int:mensagem_id>/comentarios', methods=['GET'])
def get_comentarios_por_mensagem(mensagem_id):
    comentarios = Comentario.query.filter_by(mensagem_id=mensagem_id).all()
    if not comentarios:
        return jsonify({'Mensagem': 'Nenhum comentário encontrado para essa mensagem.'}), 404
    return jsonify([cmt.json() for cmt in comentarios]), 200