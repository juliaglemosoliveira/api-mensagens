from flask import Blueprint, request, jsonify
from app import db
from app.models.usuarios import Usuario
from werkzeug.exceptions import BadRequest, Conflict, NotFound, Forbidden
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils.auth_utils import perfil_required
import re

user_bp = Blueprint('user_bp', __name__)

# Endpoint para READ-ALL
@user_bp.route('/', methods=['GET'])
@jwt_required()
@perfil_required(['ADMIN'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    return jsonify([user.json() for user in usuarios]), 200


# Endpoint para READ-ONE
@user_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def obter_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        raise NotFound("Usuário não existe, tente outro ID!")

    identidade = get_jwt_identity()  
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and usuario.id != int(identidade):
        raise Forbidden("Você não tem permissão para acessar este usuário.")

    return jsonify(usuario.json()), 200


# Endpoint para CREATE
@user_bp.route('/', methods=['POST'])
def criar_usuario():
    data = request.get_json()

    # Verifica se os campos obrigatórios existem no JSON
    if 'email' not in data or 'nome' not in data or 'senha' not in data:
        raise BadRequest("Os campos 'nome', 'email' e 'senha' devem estar presentes no corpo da requisição!")

    email = data.get('email')
    nome = data.get('nome')
    senha = data.get('senha')
    perfil = data.get('perfil')

    erros = []

    # Verifica se a senha foi enviada e tem mais de 6 caracteres
    if not senha or len(senha) <= 6:
        erros['senha'] = ["Campo obrigatório."]

    # Verifica se o email foi enviado e se tem formato válido
    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        erros["email"] = ["Campo obrigatório."]

    if erros:
        return jsonify({'errors':erros}), 422

    # Verifica se o nome não está vazio
    if not nome or not nome.strip():
        raise BadRequest('O campo nome não pode estar vazio.')

    if Usuario.query.filter_by(email=email).first():
        raise Conflict("E-mail informado já existe, por favor, tente outro!")

    novo = Usuario(email=email, nome=nome, senha=senha, perfil=perfil)
    db.session.add(novo)
    db.session.commit()

    return jsonify(novo.json()), 201


# Endpoint para UPDATE
@user_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def atualizar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        raise NotFound("Usuário não existe, tente outro ID!")
    
    data = request.get_json()

    nome = data.get('nome', usuario.nome)
    email = data.get('email', usuario.email)
    senha = data.get('senha', usuario.senha)
    
    erros = {}

    # Verifica se a senha foi enviada e tem mais de 6 caracteres
    if not senha or len(senha) <= 6:
        erros['senha'] = ["Campo obrigatório."]

    # Verifica se o email foi enviado e se tem formato válido
    if not email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        erros["email"] = ["Campo obrigatório."]

    if erros:
        return jsonify({'errors':erros}), 422
    
    email_existente = Usuario.query.filter_by(email=email).first()
    if email_existente and email_existente.id != usuario.id:
        raise Conflict("E-mail informado já existe, por favor, tente outro!")

    identidade = get_jwt_identity()  
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and usuario.id != int(identidade):
        raise Forbidden('Você não tem autorização para alterar informações desse usuário!')

    usuario.nome = nome
    usuario.email = email
    usuario.senha = senha
    db.session.commit()
    
    return jsonify({"Mensagem": "Usuário atualizado com sucesso!"}), 200


# Endpoint para DELETE
@user_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@perfil_required(['ADMIN'])
def deletar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        raise NotFound("Usuário não existe, tente outro ID!")

    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"Mensagem": "Usuário deletado com sucesso"}), 200
