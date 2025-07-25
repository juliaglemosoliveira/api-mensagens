from flask import Blueprint, jsonify, request
from app.models.mensagens import Mensagem
from app.models.usuarios import Usuario
from app import db
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.utils.auth_utils import perfil_required

#Blueprint para as mensagens
msg_bp = Blueprint('mensagens', __name__)

#Endpoint para READ - ALL
@msg_bp.route('/', methods=['GET'])
def listar_mensagens():
    #Busca por todas as mensagens no banco de dados
    mensagens = Mensagem.query.all()
    #Retorna um JSON com todas as mensagens
    return jsonify([mensagem.json() for mensagem in mensagens]), 200

#Endpoint para READ ONE
@msg_bp.route('/<int:id>', methods=['GET'])
def obter_mensagem(id):
    #Procura a mensagem no base no ID que está na URL
    mensagem = Mensagem.query.get(id)
    if mensagem:
        return jsonify(mensagem.json()), 200
    #Caso não exista, ele retorna um erro tratado
    raise NotFound("Mensagem não encontrada, tente outro ID!")

#Endpoint para CREATE
@msg_bp.route('/', methods=['POST'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def criar_mensagem():

    #Requisição enviado pelo cliente
    data = request.get_json()

    #Capitaliza as chaves enviadas na requisição, pelo cliente, evitando conflitos
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    #Verifica se realmente as chaves estão realmente presentes na requisição, se não estiver, retorna um erro tratado    
    if 'Nome' not in data_formatada or "Mensagem" not in data_formatada:
        raise BadRequest("Os campos'Nome' e 'Mensagem' devem ser preenchidos adequadamente!")
    
    #Acrescente as informações da rquisição as suas respectivas variáveis
    nome = data_formatada.get('Nome')
    mensagem = data_formatada.get('Mensagem')

    #Vericia se os campos Nome e Mensagem estão preenchidos adequadamente
    if not nome or not mensagem or not nome.strip() or not mensagem.strip():
        raise BadRequest('É obrigatório o preenchimento do nome e comentário.')
    
    #Verifica quem está autenticado
    identidade = get_jwt_identity()
    usuario_logado = identidade['id']
    
    #Adiciona os valores enviados na requisição ao banco de dados
    nova_mensagem = Mensagem(nome=data_formatada['Nome'], mensagem=data_formatada['Mensagem'], autor=usuario_logado)
    db.session.add(nova_mensagem)
    db.session.commit()
    #Retorna a mensagem que foi criada
    return jsonify(nova_mensagem.json()), 201

#Endpoint para UPDATE
@msg_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def atualizar_mensagem(id):

    #Procura a mensagem de acordo com ID enviado pelo cliente na URL
    mensagem = Mensagem.query.get(id)
    #Caso não seja encontrado a mensagem, retorna um erro tratado
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")

    #Requisição enviada pelo cliente
    data = request.get_json()

    #Capitaliza as chaves enviadas na requisição, pelo cliente, evitando conflitos
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    #Verifica se realmente as chaves estão presentes na requisição   
    if 'Mensagem' not in data_formatada or 'Nome' not in data_formatada:
        raise BadRequest("O campo deve ter obrigatoriamente os campos de 'Nome' e 'Mensagem' preenchidos adequadamente!")
    
    # Bloqueia alteração do usuário/autor, caso o cliente tente enviar a troca pela requisição
    if 'Autor' in data_formatada:
        raise BadRequest("Não é permitido alterar o autor de uma mensagem.")
    
    identidade = get_jwt_identity()
    usuario_logado = identidade['id']

    if identidade['perfil'] != 'ADMIN' and mensagem.autor != usuario_logado:
        raise Forbidden('Você não tem autorização para alterar essa mensagem!')

    #Atualiza as informações no banco de dados(caso não haja dados na requisição, permanece os valores que já estavam)
    mensagem.nome = data_formatada.get('Nome', mensagem.nome)
    mensagem.mensagem = data_formatada.get('Mensagem', mensagem.mensagem)
    db.session.commit()
    #retorna a mensagem atualizada
    return jsonify(mensagem.json()), 200

#Endpoint para DELETE
@msg_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def deletar_mensagem(id):
    #Procura a mensagem de acordo com o ID enviado pelo cliente na URL
    mensagem = Mensagem.query.get(id)
    #Caso essa mensagem existe, ela é excluída do banco de dados
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")

    identidade = get_jwt_identity()
    usuario_logado = identidade['id']

    if identidade['perfil'] != 'ADMIN' and mensagem.autor != usuario_logado:
        raise Forbidden('Você não tem permissão para apagar essa mensagem!')

    db.session.delete(mensagem)
    db.session.commit()
    #Retorna um confirmação de sucesso para a operação
    return {"Mensagem":"Mensagem excluída com sucesso!"}, 200
    