from flask import Blueprint, request, jsonify
from app import db
from app.models.comentarios import Comentario
from app.models.mensagens import Mensagem
from app.models.usuarios import Usuario
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized, Forbidden

cmt_bp = Blueprint('cmt_bp', __name__)

# Endpoint para CREATE
@cmt_bp.route('/comentarios', methods=['POST'])
def create_comentario():
    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.captalize(): valor for chave, valor in data.items()}

    # Verificando se os dados obrigatórios estão na requisição enviada
    if 'Comentario' not in data_formatada or 'Mensagem_id' not in data_formatada:
        raise BadRequest("Os campos de 'Comentario' e 'Mensagem_id' devem ser preenchidos adequadamente!")

    #Ligando os dados enviados na requisição aos seus respectivos lugares no banco de dados
    comentario = data_formatada.get('Comentario')
    mensagem_id = data_formatada.get('Mensagem_id')

    # Validação: mensagem precisa existir
    mensagem = Mensagem.query.get(mensagem_id)
    if not mensagem:
        raise NotFound('Nenhuma mensagem com esse ID, tente outro!')
    
    # Criação do comentário
    novo_comentario = Comentario(
        comentario=comentario,
        mensagem_id=mensagem_id
        )
    #Adição do novo comentário ao banco de dados
    db.session.add(novo_comentario)
    db.session.commit()

    #Retorna o comentário criado para o cliente
    return jsonify(novo_comentario.json()), 201

# Endpoint para READ ALL
@cmt_bp.route('/comentarios', methods=['GET'])
def get_comentarios():
    #Busca de todos comentários existentes no banco de dados
    comentarios = Comentario.query.all()
    return jsonify([comentario.json() for comentario in comentarios]), 200

# Endpoint para READ ONE
@cmt_bp.route('/comentarios/<int:id>', methods=['GET'])
def get_comentario(id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.get(id)
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')
    return jsonify(comentario.json()), 200

# Endpoint para UPDATE
@cmt_bp.route('/comentarios/<int:id>', methods=['PUT'])
def update_comentario(id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.get(id)
    if not comentario:
        return jsonify({'Mensagem': 'Nenhum comentário com esse ID, tente outro!'}), 404

    #Requisição enviada pelo cliente
    data = request.get_json()
    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.captalize():valor for chave, valor in data.items()}

    #Verifica se Comentario está na requsição enviada
    if 'Comentario' not in data_formatada:
        raise BadRequest("O campo 'comentario' deve ser preenchido adequadamente")

     # Bloqueia alteração de autor e mensagem_id
    if 'Autor' in data or 'Mensagem_id' in data:
        raise BadRequest('Não é permitido alterar o autor ou mensagem_id de um comentário.')
    
    #Atualização dos dados no banco de dados, caso não existe o campo na requisição, permanece o valor que já estava
    comentario.comentario = data.get('Comentario', comentario.comentario)
    db.session.commit()
    return jsonify(comentario.json()), 200

# Endpoint para DELETE
@cmt_bp.route('/comentarios/<int:id>', methods=['DELETE'])
def delete_comentario(id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.get(id)
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')
    
    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.captalize():valor for chave, valor in data.items()}

    senha_autor = data_formatada.get('Senha')
    email_autor = data_formatada.get('Email')

    #Verificação: Confere se o usuario que está tentando apagar o comentário é o autor.
    usuario = Usuario.query.filter_by(email=email_autor, senha=senha_autor).first()
    if None in usuario :
        raise Unauthorized('Senha ou email incorretos, por favor, digite-os valores corretamente.')
    
    if comentario.autor != usuario.id:
        raise Forbidden('Você não tem permissão para apagar esse comentário!')     

    #Delete o comentário do banco de dados, caso todos os requisitos sejam atendidos
    db.session.delete(comentario)
    db.session.commit()
    return jsonify({'Mensagem': 'Comentário deletado com sucesso!'}), 200

#Endpoint para Comentario por Mensagem
@cmt_bp.route('/mensagens/<int:mensagem_id>/comentarios', methods=['GET'])
def comentarios_mensagem(mensagem_id):
    #Busca por um comentário específico, com base no ID da mensagem informado na URL
    comentarios = Comentario.query.filter_by(mensagem_id=mensagem_id).all()
    if not comentarios:
        raise NotFound('Não existe nenhum comentário para essa mensagem.')
    return jsonify([comentario.json() for comentario in comentarios]), 200