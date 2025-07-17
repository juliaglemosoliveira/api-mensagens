from flask import Blueprint, jsonify, request
from app.models.mensagens import Mensagem
from app import db
from werkzeug.exceptions import NotFound, BadRequest

#Blueprint para as mensagens
msg_bp = Blueprint('mensagens', __name__)

#Endpoint para READ - ALL
@msg_bp.route('/mensagens', methods=['GET'])
def read_all():
    #Busca por todas as mensagens
    mensagens = Mensagem.query.all()
    #Retorna um JSON com todas as mensagens
    return jsonify([mensagem.json() for mensagem in mensagens]), 200

#Endpoint para READ ONE
@msg_bp.route('/mensagens/<int:id>', methods=['GET'])

def read_one(id):

    #Verifica se a mensagem existe
    mensagem = Mensagem.query.get(id)
    #Caso ela exista, retorna um json
    if mensagem:
        return jsonify(mensagem.json()), 200
    #Caso não exista, ele retorna um erro tratado
    raise NotFound("Mensagem não encontrada, tente outro ID!")

#Endpoint para CREATE
@msg_bp.route('/mensagens', methods=['POST'])
def create_mensagem():
    #JSON enviado pelo cliente
    data = request.get_json()

    #Tranforma as chaves da requisição enviada pelo cliente em minusculas, evitando conflitos.
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    
    if 'Nome' not in data_formatada or "Mensagem" not in data_formatada:
        raise BadRequest("O campo deve ter obrigatoriamente os campos de 'Nome' e 'Mensagem' preenchidos adequadamente!")

    nova_mensagem = Mensagem(nome=data_formatada['Nome'], mensagem=data_formatada['Mensagem'])
    db.session.add(nova_mensagem)
    db.session.commit()
    return jsonify(nova_mensagem.json()), 201

#Endpoint para DELETE
@msg_bp.route('/mensagens/<int:id>', methods=['DELETE'])
def delete_msg(id):
    mensagem = Mensagem.query.get(id)

    if mensagem:
        db.session.delete(mensagem)
        db.session.commit()
        return {"Mensagem":"Mensagem excluída com sucesso!"}, 200
    
    raise NotFound("Mensagem não encontrada, tente outro ID!")

#Endpoint para UPDATE
@msg_bp.route('/mensagens/<int:id>', methods=['PUT'])
def upadte_msg(id):
    mensagem = Mensagem.query.get(id)
    data = request.get_json()
    if not data:
        raise BadRequest({"Mensagem":"Os dados enviados devem estar no formato adequado(JSON)"})
    
     # Bloqueia alteração do usuário/autor
    if 'usuario' in data:
        raise BadRequest({"Mensagem": "Não é permitido alterar o autor de uma mensagem."})

    if mensagem:
        mensagem.nome = data.get('nome', mensagem.nome)
        mensagem.mensagem = data.get('mensagem', mensagem.mensagem)

        db.session.commit()
        return jsonify(mensagem.json()), 200
    raise NotFound({"Mensagem":"Mensagem não encontrada, tente outro ID!"})

