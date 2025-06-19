from flask import Blueprint, request, jsonify
from email_validator import validate_email, EmailNotValidError
from app import db
from models.usuario import Usuario
from models.usuario import validar_senha

user_bp = Blueprint('user_bp', __name__)

#CREATE
@user_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    data = request.get_json()

    email = data.get('email')
    nome = data.get('nome')
    senha = data.get('senha')

    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    try:
        validate_email(email)  # Valida formato do email
    except EmailNotValidError:
        return jsonify({'erro': 'Email inválido'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'erro': 'Email já cadastrado'}), 400

    if not validar_senha(senha):
        return jsonify({'erro': 'Senha fraca. Deve ter 8 caracteres, número, maiúscula, minúscula e especial.'}), 400

    novo = Usuario(email=email, nome=nome, senha=senha)
    db.session.add(novo)
    db.session.commit()

    return jsonify({'mensagem': 'Usuário criado com sucesso', 'id': novo.id}), 201

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
    usuario = Usuario.query.get_or_404(id)
    return jsonify({
        'id': usuario.id,
        'email': usuario.email,
        'nome': usuario.nome
    })

# --------------------------
# UPDATE - Atualizar usuário
# --------------------------
@user_bp.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    data = request.get_json()

    nome = data.get('nome', usuario.nome)
    email = data.get('email', usuario.email)
    senha = data.get('senha', usuario.senha)

    if not nome:
        return jsonify({'erro': 'Nome é obrigatório'}), 400

    try:
        validate_email(email)
    except EmailNotValidError:
        return jsonify({'erro': 'Email inválido'}), 400

    email_existente = Usuario.query.filter_by(email=email).first()
    if email_existente and email_existente.id != id:
        return jsonify({'erro': 'Email já cadastrado por outro usuário'}), 400

    if senha != usuario.senha and not validar_senha(senha):
        return jsonify({'erro': 'Senha fraca'}), 400

    usuario.nome = nome
    usuario.email = email
    usuario.senha = senha

    db.session.commit()

    return jsonify({'mensagem': 'Usuário atualizado com sucesso'})

@user_bp.route('/usuarios/<int:id>', methods=['DELETE'])
def deletar_usuario(id):
    usuario = Usuario.query.get_or_404(id)
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({'mensagem': 'Usuário deletado com sucesso'})