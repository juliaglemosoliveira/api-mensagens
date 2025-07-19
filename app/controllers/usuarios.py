from flask import Blueprint, request, jsonify
from app import db
from app.models.usuarios import Usuario
from app.utils.utils import validar_email, validar_senha
from werkzeug.exceptions import BadRequest, Conflict, NotFound

user_bp = Blueprint('user_bp', __name__)

#Endpoint para CREATE
@user_bp.route('/usuarios', methods=['POST'])
def criar_usuario():
    #Requisição enviada pelo cliente
    data = request.get_json()

    #Pega os dados enviados pelo cliente na requisição e adiciona aos seus respectivos lugares no banco de dados
    email = data.get('email')
    nome = data.get('nome')
    senha = data.get('senha')

    #Lista de erros, sendo o lugar onde será adicionado os erros que forem surgindo, para retornar todos de uma única vez(Caso seja mais de um)
    erros = []

    #validação de email
    email_valido = validar_email(email)
     #Se o e-mail não estiver dentro dos requisitos, ele adiciona esse erro a lista ERROS
    if email_valido is not True:
        erros.append(email_valido)
    
    #validação da senha
    senha_valida = validar_senha(senha)
    #Se a senha não estiver dentro dos requisitos, ele adiciona esse erro a lista ERROS
    if senha_valida is not True:
        erros.append(senha_valida)
    
    #Caso existe algum erro dentro da lista ERROS, todos serão retornados pra o cliente
    if erros:
       raise BadRequest(erros)

    #Verifica se o e-mail já existe no banco de dados, caso já exista, ele retorna essa informação ao cliente
    if Usuario.query.filter_by(email=email).first():
        raise Conflict("E-mail já existe, por favor, tente outro!")

    #Se todos os requisitos forem atendidos, é adicionado um novo usuário ao banco de dados
    novo = Usuario(email=email, nome=nome, senha=senha)
    db.session.add(novo)
    db.session.commit()

    #Retorna o usuário que foi adicionado para o cliente
    return jsonify(novo.json()), 201

#Endpoint para READ-ALL
@user_bp.route('/usuarios', methods=['GET'])
def listar_usuarios():
    #Procura todos os usuarios existentes no banco de dados
    usuarios = Usuario.query.all()
    #Retorna todos os usuários que estão no banco de dados no formato JSON
    return jsonify([user.json() for user in usuarios]), 200

# Endpoint para READ-ONE
@user_bp.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    #Procura um usuário especifico, de acordo com o ID que estiver na URL
    usuario = Usuario.query.get(id)
    #Se esse usuário realmente existir, retorna ele em formato JSON
    if usuario:
        return jsonify(usuario.json()), 200
    #Caso não exista, é retornado um erro tratado
    raise NotFound("Usuário não existe, tente outro ID!")

#Endpoint para UPDATE
@user_bp.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    #Procura um usuário especifico, de acordo com o ID que estiver na UR
    usuario = Usuario.query.get(id)
    #Caso não exista, é retornado um erro tratado
    if not usuario:
        raise BadRequest("Usuário não existe, tente outro ID!")
     #Requisição enviada pelo cliente
    data = request.get_json()
    
    #Acrescenta as novas informações aos seus respectivos locais, caso não haja dados na informação, permanece o valor que já está
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
        raise BadRequest(erros)

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
    
    raise BadRequest("Usuário não existe, tente outro ID!")