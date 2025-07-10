from flask import Blueprint, request, jsonify
from app import db
from app.models.usuarios import Usuario
from app.utils.utils import validar_email, validar_senha

user_bp = Blueprint('user_bp', __name__)

#Endpoint para CREATE
@user_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    data = request.get_json()

    email = data.get('email')
    nome = data.get('nome')
    senha = data.get('senha')

    erros = []

    #validação de email
    email_valido = validar_email(email)
    if email_valido is not True:
        erros.append(email_valido)
    
    #validação da senha
    senha_valida = validar_senha(senha)
    if senha_valida is not True:
        erros.append(senha_valida)
    
    if erros:
        return jsonify({"erros":erros}), 400

    if Usuario.query.filter_by(email=email).first():
        return {"Mensagem":"E-mail já existe, por favor, tente outro!"}, 409

    novo = Usuario(email=email, nome=nome, senha=senha)
    db.session.add(novo)
    db.session.commit()

    return jsonify(novo.json()), 201

#Endpoint para READ-ALL
@user_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    
    return jsonify([user.json() for user in usuarios]), 200

# Endpoint para READ-ONE
@user_bp.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario:
        return jsonify(usuario.json()), 200
    
    return jsonify({"Mensagem":"Usuário não existe, tente outro ID!"}), 404

#Endpoint para UPDATE
@user_bp.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"Mensagem":"Usuário não existe, tente outro ID!"}), 404
    
    data = request.get_json()

    if not data:
        return jsonify({"Mensagem":"Os dados enviados devem estar no formato adequado(JSON)"}), 400

    nome = data.get('nome', usuario.nome)
    email = data.get('email', usuario.email)
    senha = data.get('senha', usuario.senha)

    erros = []

     #validação de email
    email_valido = validar_email(email)
    if email_valido is not True:
        erros.append(email_valido)
    
    #validação da senha
    senha_valida = validar_senha(senha)
    if senha_valida is not True:
        erros.append(senha_valida)

    if erros:
        return jsonify({"erros":erros}), 400

    usuario.nome = nome
    usuario.email = email
    usuario.senha = senha

    db.session.commit()

    return jsonify({"Mensagem":"Usuário atualizado com sucesso!"}), 200

@user_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario:

        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"Mensagem":"Usuário deletado com sucesso"}), 200
    
    return jsonify({"Mensagem":"Usuário não existe, tente outro ID!"})