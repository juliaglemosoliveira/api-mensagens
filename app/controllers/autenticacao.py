
from flask import Blueprint, request, jsonify
from app.models.usuarios import Usuario
from app.models.tokens import Token
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt, get_jti
from app import db
from werkzeug.exceptions import Unauthorized, Forbidden

auth_bp = Blueprint('auth_bp', __name__)

# Login
@auth_bp.route('/login', methods=['POST'])
def login():
    #Requisição enviada pelo cliente
    data = request.get_json()
    #Ligando as informações enviadas na requisição com suas respectivas variáveis
    email = data.get('email')
    senha = data.get('senha')
    #Verifica se o usuário realmente existe no banco de dados
    usuario = Usuario.query.filter_by(email=email, senha=senha).first()
    if not usuario:
        raise Unauthorized('Credenciais inválidas.')
    #Cria um Token de acesso e de atualização para o usuário logado
    access_token = create_access_token(identity={'id': usuario.id, 'perfil': usuario.perfil})
    refresh_token = create_refresh_token(identity={'id': usuario.id, 'perfil': usuario.perfil})
    #Adiciona o Token Refresh ao banco de dados, para ser possível a rotação
    add_token = Token(token=refresh_token, usuario_id=usuario.id)
    db.session.add(add_token)
    db.session.commit()

    return jsonify(access_token=access_token, refresh_token=refresh_token), 200

# REFRESH
@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    #Pega o token enviado decodifica
    token = get_jwt()
    #Pega o identificador único do token
    jti = token['jti']
    #Pega os dados de identidade que foram definidios no token
    identidade = get_jwt_identity()
    #Pega, especificamente, o ID
    usuario_id = identidade['id']

    #Verifica o ID do token que está no banco de dados
    token_db = Token.query.filter_by(jti=jti).first()

    # Se o ID que estiver no DB não for o mesmo do token enviado na requisição, ou o token enviado estiver inválido, é retornado um erro tratado.
    if not token_db or not token_db.valido:
        raise Forbidden('Token enviado não é valido.')
    
    #Caso o Token seja valido e coincida com o ID que está no DB, então invalida o token antigo
    token_db.valido = False

    #Cria uma novo Refresh Token
    new_refresh_token = create_refresh_token(identity=identidade)
    
    new_jti = get_jti(new_refresh_token)
    add_token = Token(token=new_jti, usuario_id=usuario_id)
    db.session.add(add_token)
    db.session.commit()

    new_access_token = create_access_token(identity=identidade)
    return jsonify(access_token=new_access_token, refresh_token=new_refresh_token ), 200