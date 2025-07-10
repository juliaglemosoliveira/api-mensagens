from flask import Blueprint, request, jsonify
from app import db
from app.models.comentarios import Comentario
from app.models.mensagens import Mensagem
from app.models.usuarios import Usuario

cmt_bp = Blueprint('cmt_bp', __name__)
# Endpoint para CREATE
@cmt_bp.route('/comentarios', methods=['POST'])
def create_comentario():

    data = request.get_json()
    if not data:
        return jsonify({"Mensagem":"Os dados enviados devem estar no formato adequado(JSON)"}), 400

    data_formatada = {chave.lower(): valor for chave, valor in data.items()}
    campos_obrigatorios = ['comentario', 'mensagem_id']

    if not all(campo in data_formatada for campo in campos_obrigatorios):
        return jsonify({'Mensagem': "Os campos de 'comentario' e 'mensagem_id' devem ser preenchidos adequadamente!"}), 400

    

    comentario = data_formatada.get('comentario')
    mensagem_id = data_formatada.get('mensagem_id')

    # Validação: mensagem precisa existir
    mensagem = Mensagem.query.get(mensagem_id)
    if not mensagem:
        return jsonify({'Mensagem': 'Nenhuma mensagem com esse ID, tente outro!'}), 404

    # Criação do comentário
    novo_comentario = Comentario(
        comentario=comentario,
        mensagem_id=mensagem_id
        )

    db.session.add(novo_comentario)
    db.session.commit()

    return jsonify(novo_comentario.json()), 201

# Endpoint para READ ALL
@cmt_bp.route('/comentarios', methods=['GET'])
def get_comentarios():
    comentarios = Comentario.query.all()
    return jsonify([comentario.json() for comentario in comentarios]), 200

# Endpoint para READ ONE
@cmt_bp.route('/comentarios/<int:id>', methods=['GET'])
def get_comentario(id):
    comentario = Comentario.query.get(id)
    if not comentario:
        return jsonify({'Mensagem': 'Nenhum comentário com esse ID, tente outro!'}), 404
    return jsonify(comentario.json()), 200

# Endpoint para UPDATE
@cmt_bp.route('/comentarios/<int:id>', methods=['PUT'])
def update_comentario(id):
    comentario = Comentario.query.get(id)
    if not comentario:
        return jsonify({'Mensagem': 'Nenhum comentário com esse ID, tente outro!'}), 404

    data = request.get_json()
    data_formatada = {chave.lower():valor for chave, valor in data.items()}

    if 'comentario' not in data_formatada:
        return jsonify({'Mensagem':"O campo 'comentario' deve ser preenchido adequadamente"})

     # Bloqueia alteração de autor e mensagem_id
    if 'autor' in data or 'mensagem_id' in data:
        return jsonify({'Mensagem': 'Não é permitido alterar o autor ou mensagem_id de um comentário.'}), 400

    comentario.comentario = data.get('comentario', comentario.comentario)
    db.session.commit()
    return jsonify(comentario.json()), 200

# Endpoint para DELETE
@cmt_bp.route('/comentarios/<int:id>', methods=['DELETE'])
def delete_comentario(id):
    comentario = Comentario.query.get(id)
    if not comentario:
        return jsonify({'Mensagem': 'Nenhum comentário com esse ID, tente outro!'}), 404
    
    data = request.get_json()
    senha_autor = data.get('senha')
    email_autor = data.get('email')

    #Verificação: Confere se o usuario que está tentando apagar o comentário é o autor.
    usuario = Usuario.query.filter_by(email=email_autor, senha=senha_autor).first()
    if None in usuario :
        return jsonify({'Mensagem': 'Senha ou email incorretos, por favor, digite-os valores corretamente.'}), 400
    
    if comentario.autor != usuario.id:
        return jsonify({'Mensagem': 'Você não tem permissão para apagar esse comentário!'}), 403        

    db.session.delete(comentario)
    db.session.commit()
    return jsonify({'Mensagem': 'Comentário deletado com sucesso!'}), 200

#Endpoint para Comentario por Mensagem
@cmt_bp.route('/mensagens/<int:mensagem_id>/comentarios', methods=['GET'])
def comentarios_mensagem(mensagem_id):
    comentarios = Comentario.query.filter_by(mensagem_id=mensagem_id).all()
    if not comentarios:
        return jsonify({'Mensagem': 'Nenhum comentário encontrado para essa mensagem.'}), 404
    return jsonify([comentario.json() for comentario in comentarios]), 200