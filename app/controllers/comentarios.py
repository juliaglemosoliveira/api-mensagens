from flask import Blueprint, request, jsonify
from app import db
from app.models.comentarios import Comentario
from app.models.mensagens import Mensagem
from app.models.usuarios import Usuario
from werkzeug.exceptions import BadRequest, NotFound, Unauthorized, Forbidden
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils.auth_utils import perfil_required 

cmt_bp = Blueprint('cmt_bp', __name__)

# Endpoint para READ ALL
@cmt_bp.route('/', methods=['GET'])
@jwt_required()
@perfil_required(['ADMIN'])
def listar_comentarios():
    #Busca de todos comentários existentes no banco de dados
    comentarios = Comentario.query.all()
    #Retorna todos os comentários existentes no formato JSON
    return jsonify([comentario.json() for comentario in comentarios]), 200

# Endpoint para READ ONE
@cmt_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def obter_comentario(id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.get(id)
    #Caso esse comentário não exista, retorna um erro tratado
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')

    # ID do usuário autenticado
    identidade = get_jwt_identity()  
    claims = get_jwt()
    perfil = claims.get('perfil')

    # Se não for ADMIN e tentar acessar outro usuário
    if perfil != 'ADMIN' and comentario.autor != int(identidade):
        raise Forbidden("Você não tem permissão para acessar este comentario.")

    return jsonify(comentario.json()), 200

# Endpoint para CREATE
@cmt_bp.route('/', methods=['POST'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def criar_comentario():
    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    # Verificando se os dados obrigatórios estão na requisição enviada
    if 'Comentario' not in data_formatada or 'Mensagem_id' not in data_formatada:
        raise BadRequest("Os campos de 'Comentario' e 'Mensagem_id' devem ser preenchidos adequadamente!")

    #Acrescente as informações da requisição as suas respectivas variáveis
    comentario = data_formatada.get('Comentario')
    mensagem_id = data_formatada.get('Mensagem_id')

    # Verifica se a mensagem para qual o comentário é destinado realmente exite
    mensagem = Mensagem.query.get(mensagem_id)
    if not mensagem:
        raise NotFound('Nenhuma mensagem com esse ID, tente outro!')

    identidade = get_jwt_identity()
    
    #Adição do novo comentário ao banco de dados
    novo_comentario = Comentario(comentario=comentario,mensagem_id=mensagem_id, autor=identidade)
    db.session.add(novo_comentario)
    db.session.commit()
    #Retorna o comentário criado para o cliente
    return jsonify(novo_comentario.json()), 201


# Endpoint para UPDATE
@cmt_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def atualizar_comentario(id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.get(id)
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')

    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.capitalize():valor for chave, valor in data.items()}

    #Verifica se Comentario está na requsição enviada
    if 'Comentario' not in data_formatada:
        raise BadRequest("O campo 'comentario' deve ser preenchido adequadamente")

     # Bloqueia alteração de autor e mensagem_id
    if 'Autor' in data or 'Mensagem_id' in data:
        raise BadRequest('Não é permitido alterar o autor ou mensagem_id de um comentário.')
    
    identidade = get_jwt_identity()
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and comentario.autor != int(identidade):
        raise Forbidden('Você não tem autorização para alterar esse comentário!')
    
     #Atualiza as informações no banco de dados(caso não haja dados na requisição, permanece os valores que já estavam)
    comentario.comentario = data_formatada.get('Comentario', comentario.comentario)
    db.session.commit()
    return jsonify(comentario.json()), 200

# Endpoint para DELETE
@cmt_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def deletar_comentario(id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.get(id)
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')
    
    identidade = get_jwt_identity()
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and comentario.autor != int(identidade):
        raise Forbidden('Você não tem autorização para deletar esse comentário!')
   
    #Delete o comentário do banco de dados, caso todos os requisitos sejam atendidos
    db.session.delete(comentario)
    db.session.commit()
    return jsonify({'Mensagem': 'Comentário deletado com sucesso!'}), 200

#Endpoint para Comentario por Mensagem
@cmt_bp.route('/<int:mensagem_id>/comentarios', methods=['GET'])
def comentarios_por_mensagem(mensagem_id):
    #Busca por um comentário específico, com base no ID da mensagem informado na URL
    comentarios = Comentario.query.filter_by(mensagem_id=mensagem_id).all()
    if not comentarios:
        raise NotFound('Não existe nenhum comentário para essa mensagem.')
    #Retorna todos os comentários que existem para aquela mensagem no formato JSON
    return jsonify([comentario.json() for comentario in comentarios]), 200