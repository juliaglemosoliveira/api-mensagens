from flask import Blueprint, request, jsonify
from app import db
from app.models.usuarios import Usuario
from app.utils.utils import validar_email, validar_senha
from werkzeug.exceptions import BadRequest, Conflict, NotFound, Unauthorized, Forbidden
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.utils.auth_utils import perfil_required

user_bp = Blueprint('user_bp', __name__)

#Endpoint para READ-ALL
@user_bp.route('/', methods=['GET'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def listar_usuarios():

    identidade = get_jwt()
    if 'ADMIN' not in additional_claims:
        raise Forbidden('Você não tem autorização para acessar esse recurso!')
    
    #Procura todos os usuarios existentes no banco de dados
    usuarios = Usuario.query.all()

    #Retorna todos os usuários que estão no banco de dados no formato JSON
    return jsonify([user.json() for user in usuarios]), 200


# Endpoint para READ-ONE
@user_bp.route('/<int:id>', methods=['GET'])
def obter_usuario(id):
    #Procura um usuário especifico, de acordo com o ID que estiver na URL
    usuario = Usuario.query.get(id)
    if usuario:
        return jsonify(usuario.json()), 200
    #Caso não exista, é retornado um erro tratado
    raise NotFound("Usuário não existe, tente outro ID!")

#Endpoint para CREATE
@user_bp.route('/', methods=['POST'])
def criar_usuario():
    #Requisição enviada pelo cliente
    data = request.get_json()

    #Capitaliza as chaves enviadas na requisição, pelo cliente, evitando conflitos
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    #Acrescente as informações da requisição as suas respectivas variáveis
    email = data_formatada.get('Email')
    nome = data_formatada.get('Nome')
    senha = data_formatada.get('Senha')

    #Verifica se Email, Nome e Senha estão na requisição
    if 'Email' not in data_formatada or 'Nome' not in data_formatada or 'Senha' not in data_formatada:
        raise BadRequest("Os campos'Nome', 'Email' e 'Senha' devem ser preenchidos adequadamente!")
    
    #Verifica se nome está vazio
    if not nome or not nome.strip():
        raise BadRequest('É obrigatório o preenchimento do nome.')

    #Lista de erros, sendo o lugar onde será adicionado os erros que forem surgindo, para retornar todos de uma única vez(Caso haja mais de um)
    erros = []

    #validação de email
    email_valido = validar_email(email)
    if email_valido is not True:
        erros.append(email_valido)
    
    #validação da senha
    senha_valida = validar_senha(senha)
    if senha_valida is not True:
        erros.append(senha_valida)
    
    #Caso existe algum erro dentro da lista ERROS, todos serão retornados pra o cliente
    if erros:
       raise BadRequest(erros)

    #Verifica se o e-mail já existe
    if Usuario.query.filter_by(email=email).first():
        raise Conflict("E-mail informado já existe, por favor, tente outro!")

    #Se todos os requisitos forem atendidos, é adicionado um novo usuário ao banco de dados
    novo = Usuario(email=email, nome=nome, senha=senha)
    db.session.add(novo)
    db.session.commit()

    #Retorna o usuário que foi adicionado para o cliente
    return jsonify(novo.json()), 201

#Endpoint para UPDATE
@user_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def atualizar_usuario(id):
    #Procura um usuário especifico, de acordo com o ID que estiver na URL
    usuario = Usuario.query.get(id)
    if not usuario:
        raise BadRequest("Usuário não existe, tente outro ID!")
    
    #Capitaliza as chaves enviadas na requisição pelo cliente, evitando erros
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    #Requisição enviada pelo cliente
    data = request.get_json()
    
    #Acrescenta as novas informações enviadas na requisição as suas respectivas variáveis(caso não haja dados na informação, permanece o valor que já está)
    nome = data_formatada.get('Nome', usuario.nome)
    email = data_formatada.get('Email', usuario.email)
    senha = data_formatada.get('Senha', usuario.senha)
    
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
        raise BadRequest(erros)

    identidade = get_jwt_identity()
    usuario_logado = identidade['id']

    if identidade['perfil'] != 'ADMIN' and usuario.id != usuario_logado:
        raise Forbidden('Você não tem autorização para alterar informações desse usuário!')

    #Atualiza os campos do banco de dados com as novas informações
    usuario.nome = nome
    usuario.email = email
    usuario.senha = senha
    db.session.commit()
    return jsonify({"Mensagem":"Usuário atualizado com sucesso!"}), 200

#Endpoint para DELETE
@user_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def deletar_usuario(id):
    #Procura um usuário especifico, de acordo com o ID que estiver na URL
    usuario = Usuario.query.get(id)
    if not usuario:
        raise BadRequest("Usuário não existe, tente outro ID!")

    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.capitalize():valor for chave, valor in data.items()}

    #Acrescente as informações da requisição as suas respectivas variáveis
    senha_autor = data_formatada.get('Senha')
    email_autor = data_formatada.get('Email')

    identidade = get_jwt_identity()
    usuario_logado = identidade['id']

    if identidade['perfil'] != 'ADMIN' and usuario.id != usuario_logado:
        raise Forbidden('Você não tem autorização para deletar esse usuário!')

    #Apaga o usuário do banco de dados
    db.session.delete(usuario)
    db.session.commit()
    return jsonify({"Mensagem":"Usuário deletado com sucesso"}), 200
    
    