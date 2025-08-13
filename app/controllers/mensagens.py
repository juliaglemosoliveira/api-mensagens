from flask import Blueprint, jsonify, request
from app.models.mensagens import Mensagem
from app.models.comentarios import Comentario
from app import db
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils.auth_utils import perfil_required

msg_bp = Blueprint('msg_bp', __name__)

# READ - ALL
@msg_bp.route('/', methods=['GET'])
def listar_mensagens():
    mensagens = Mensagem.query.all()
    return jsonify([mensagem.json() for mensagem in mensagens]), 200

# READ ONE
@msg_bp.route('/<int:id>', methods=['GET'])
def obter_mensagem(id):
    mensagem = Mensagem.query.get(id)
    if mensagem:
        return jsonify(mensagem.json()), 200
    raise NotFound("Mensagem não encontrada, tente outro ID!")

# CREATE
@msg_bp.route('/', methods=['POST'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def criar_mensagem():
    data = request.get_json()

    if 'titulo' not in data or 'conteudo' not in data:
        raise BadRequest("Os campos 'titulo' e 'conteudo' são obrigatórios no corpo da requisição!")


    token = get_jwt()
    if not token:
        raise Unauthorized('Token JWT ausente ou inválido.')
    
    titulo = data.get('titulo')
    conteudo = data.get('conteudo')

    if not titulo or not conteudo or not titulo.strip() or not conteudo.strip():
        return jsonify({"errors": {"titulo": ["Campo obrigatório."], "conteudo":["Campo obrigatório."]}}), 422

    identidade = get_jwt_identity()

    nova_mensagem = Mensagem(titulo=titulo, conteudo=conteudo, autor=identidade)
    db.session.add(nova_mensagem)
    db.session.commit()

    return jsonify(nova_mensagem.json()), 201

# UPDATE
@msg_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def atualizar_mensagem(id):
    mensagem = Mensagem.query.get(id)
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")

    data = request.get_json()

    identidade = get_jwt_identity()
    token = get_jwt()
    perfil = token.get('perfil')

    titulo = data.get('titulo')
    conteudo = data.get('conteudo')

    if not titulo or not conteudo or not titulo.strip() or not conteudo.strip():
        return jsonify({"errors": {"titulo": ["Campo obrigatório."], "conteudo":["Campo obrigatório."]}}), 422

    if 'autor' in data:
        raise BadRequest("Não é permitido alterar o autor de uma mensagem.")

    if not token:
        raise Unauthorized('Token JWT ausente ou inválido')

    if perfil != 'ADMIN' and mensagem.autor != int(identidade):
        raise Forbidden('Você não tem autorização para alterar esta mensagem!')
    
    mensagem.titulo = titulo
    mensagem.conteudo = conteudo
    db.session.commit()

    return jsonify(mensagem.json()), 200

# UPDATE PARCIAL
@msg_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def modificar_mensagem(id):
    mensagem = Mensagem.query.get(id)
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")

    data = request.get_json()

    identidade = get_jwt_identity()
    token = get_jwt()
    perfil = token.get('perfil')

    conteudo = data.get('conteudo')

    if not conteudo or not conteudo.strip():
        return jsonify({"errors": {"titulo": ["Campo obrigatório."]}}), 422

    if 'autor' in data or 'titulo' in data:
        raise BadRequest("Não é permitido alterar o autor ou titulo de uma mensagem por esse método.")

    if not token:
        raise Unauthorized('Token JWT ausente ou inválido')

    if perfil != 'ADMIN' and mensagem.autor != int(identidade):
        raise Forbidden('Você não tem autorização para alterar essa mensagem!')

    mensagem.conteudo = conteudo
    db.session.commit()

    return jsonify(mensagem.json()), 200

# DELETE
@msg_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def deletar_mensagem(id):
    mensagem = Mensagem.query.get(id)
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")

    identidade = get_jwt_identity()
    token = get_jwt()
    perfil = token.get('perfil')

    if not token:
        return jsonify({"error": "Token JWT ausente ou inválido"}), 422

    if perfil != 'ADMIN' and mensagem.autor != int(identidade):
        raise Forbidden('Você não tem permissão para apagar essa mensagem!')

    db.session.delete(mensagem)
    db.session.commit()
    return {"Mensagem": "Mensagem excluída com sucesso!"}, 200

# Comentários - READ
@msg_bp.route('/<int:mensagem_id>/comentarios', methods=['GET'])
def comentarios_por_mensagem(mensagem_id):
    comentarios = Comentario.query.filter_by(mensagem_id=mensagem_id).all()
    if not comentarios:
        raise NotFound('Não existe nenhum comentário para essa mensagem.')
    return jsonify([comentario.json() for comentario in comentarios]), 200

# Comentários - CREATE
@msg_bp.route('/<int:mensagem_id>/comentarios', methods=['POST'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def criar_comentario(mensagem_id):
    data = request.get_json()

    conteudo = data.get('conteudo')

    identidade = get_jwt_identity()
    token = get_jwt()

    mensagem = Mensagem.query.get(mensagem_id)
    if not mensagem:
        raise NotFound('Nenhuma mensagem com esse ID, tente outro!')
    
    if 'conteudo' not in data:
        raise BadRequest("O campo 'conteudo' deve ser preenchido adequadamente!")

    if not token:
        raise Unauthorized({"Token JWT ausente ou inválido"})
    
    if not conteudo or not conteudo.strip():
        return jsonify({"errors": {"conteudo": ["Campo obrigatório."]}}), 422

    novo_comentario = Comentario(conteudo=conteudo, mensagem_id=mensagem_id, autor=identidade)
    db.session.add(novo_comentario)
    db.session.commit()

    return jsonify(novo_comentario.json()), 201

# Comentários - UPDATE
@msg_bp.route('/<int:mensagem_id>/comentarios/<int:comentario_id>', methods=['PUT'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def atualizar_comentario(mensagem_id, comentario_id):
    comentario = Comentario.query.filter_by(mensagem_id=mensagem_id, id=comentario_id).first()
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')

    data = request.get_json()

    conteudo = data.get('conteudo')

    identidade = get_jwt_identity()
    token = get_jwt()
    perfil = token.get('perfil')

    if 'conteudo' not in data:
        raise BadRequest("O campo 'conteudo' deve ser preenchido adequadamente")
    
    if 'autor' in data or 'mensagem_id' in data:
        raise BadRequest('Não é permitido alterar o autor ou mensagem_id de um comentário.')

    if not token:
        raise Unauthorized("Token JWT ausente ou inválido")
    
    if not conteudo or not conteudo.strip():
        return jsonify({"errors": {"conteudo": ["Campo obrigatório."]}}), 422

    if perfil != 'ADMIN' and comentario.autor != int(identidade):
        raise Forbidden('Você não tem permissão para alterar esse comentário!')

    comentario.conteudo = conteudo
    db.session.commit()
    return jsonify(comentario.json()), 200

# Comentários - DELETE
@msg_bp.route('/<int:mensagem_id>/comentarios/<int:comentario_id>', methods=['DELETE'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def deletar_comentario(mensagem_id, comentario_id):
    comentario = Comentario.query.filter_by(mensagem_id=mensagem_id, id=comentario_id).first()
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')

    identidade = get_jwt_identity()
    token = get_jwt()
    perfil = token.get('perfil')

    if not token:
        raise Unauthorized('Token JWT ausente ou inválido.')

    if perfil != 'ADMIN' and comentario.autor != int(identidade):
        raise Forbidden('Você não tem autorização para deletar esse comentário!')

    db.session.delete(comentario)
    db.session.commit()
    return jsonify({'Mensagem': 'Comentário deletado com sucesso!'}), 200