from flask import Blueprint, request, jsonify
from app.models.usuarios import Usuario
from flask_jwt_extended import (
    create_access_token, create_refresh_token, jwt_required,
    get_jwt_identity, get_jwt
)
from app import db
from werkzeug.exceptions import Unauthorized

auth_bp = Blueprint('auth_bp', __name__)

# LOGIN
@auth_bp.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    senha = data.get('senha')
    usuario = Usuario.query.filter_by(email=email, senha=senha).first()
    if not usuario:
        raise Unauthorized('Credenciais inválidas.')
    access_token = create_access_token(identity={'id': usuario.id, 'perfil': usuario.perfil})
    refresh_token = create_refresh_token(identity={'id': usuario.id, 'perfil': usuario.perfil})
    # Opcional: Salvar refresh_token no banco, se quiser rotação
    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

# REFRESH
@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    identidade = get_jwt_identity()
    access_token = create_access_token(identity=identidade)
    return jsonify(access_token=access_token), 200