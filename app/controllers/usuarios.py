from flask import Blueprint, request, jsonify
from app import db
from app.models.usuarios import Usuario

user_bp = Blueprint('user_bp', __name__)

#CREATE
@user_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    data = request.get_json()

    email = data.get('email')
    nome = data.get('nome')
    senha = data.get('senha')

    erros = []

    #validação de email
    email_valido = Usuario.validar_email(email)
    if email_valido is not True:
        erros.append(email_valido)
    
    #validação da senha
    senha_valida = Usuario.validar_senha(senha)
    if senha_valida is not True:
        erros.append(senha_valida)
    
    if erros:
        return jsonify({"erros":erros}), 400

    if Usuario.query.filter_by(email=email).first():
        return {"mensagem":"E-mail já existente, por favor, tente outro!"}, 400

    novo = Usuario(email=email, nome=nome, senha=senha)
    db.session.add(novo)
    db.session.commit()

    return jsonify(novo.json()), 201

# --------------------------
# READ - Buscar todos os usuários
# --------------------------
@user_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = Usuario.query.all()
    resultado = []
    for u in usuarios:
        resultado.append({
            'id': u.id,
            'email': u.email,
            'nome': u.nome
        })
    return jsonify(resultado)

# --------------------------
# READ - Buscar usuário por ID
# --------------------------
@user_bp.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario:
        return jsonify(usuario.json()), 200
    return jsonify({"mensagem": "Nenhum usuário encontrado referente a esse ID , tente outro, por favor!"})

# --------------------------
# UPDATE - Atualizar usuário
# --------------------------
@user_bp.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    usuario = Usuario.query.get(id)
    if not usuario:
        return jsonify({"mensagem":"usuário com esse ID não existe!"}), 404
    
    data = request.get_json()

    nome = data.get('nome', usuario.nome)
    email = data.get('email', usuario.email)
    senha = data.get('senha', usuario.senha)

    erros = []

     #validação de email
    email_valido = Usuario.validar_email(email)
    if email_valido is not True:
        erros.append(email_valido)
    
    #validação da senha
    senha_valida = Usuario.validar_senha(senha)
    if senha_valida is not True:
        erros.append(senha_valida)

    if erros:
        return jsonify({"erros":erros}), 400

    usuario.nome = nome
    usuario.email = email
    usuario.senha = senha

    db.session.commit()

    return jsonify({'mensagem': 'Usuário atualizado com sucesso'})

@user_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    usuario = Usuario.query.get(id)

    if usuario:

        db.session.delete(usuario)
        db.session.commit()
        return jsonify({'mensagem': 'Usuário deletado com sucesso'})
    
    return jsonify({"mensagem":"Nenhum usuário encontrado referente a esse ID , tente outro, por favor!"})