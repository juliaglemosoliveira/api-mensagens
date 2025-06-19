from flask import Blueprint, jsonify, request
from app.models.mensagens import Entrada
from app import db

msg_bp = Blueprint('mensagens', __name__)

#Endpoint para READ - ALL
@msg_bp.route('/mensagens', methods=['GET'])
def read_all():
    mensagens = Entrada.query.all()
    return jsonify([mensagem.json() for mensagem in mensagens]), 200

#Endpoint para READ ONE
@msg_bp.route('/mensagens/<int:id>', methods=['GET'])
def read_one(id):
    mensagem = Entrada.query.get(id)

    if mensagem:
        return jsonify(mensagem.json()), 200
    
    return {"Mensagem": "ID não encontrado, tente outro!"}, 404

#Endpoint para CREATE
@msg_bp.route('/mensagens', methods=['POST'])
def create_mensagem():
    data = request.get_json()
    nova_mensagem = Entrada(nome=data['nome'], mensagem=data['mensagem'])
    db.session.add(nova_mensagem)
    db.session.commit()
    return jsonify(nova_mensagem.json()), 201

#Endpoint para DELETE
@msg_bp.route('/mensagens/<int:id>', methods=['DELETE'])
def delete_msg(id):
    mensagem = Entrada.query.get(id)

    if mensagem:
        db.session.delete(mensagem)
        db.session.commit()
        return {"Mensagem": "Mensagem excluída com sucesso!"}
    
    return {"Mensagem": "Mensagem não encontrada, tente outro ID!"}

#Endpoint para UPDATE
@msg_bp.route('/mensagens/<int:id>', methods=['PUT'])
def upadte_msg(id):
    data = request.get_json()
    mensagem = Entrada.query.get(id)
    
    mensagem.nome = data.get('nome', mensagem.nome)
    mensagem.mensagem = data.get('mensagem', mensagem.mensagem)

    db.session.commit()
    return jsonify(mensagem.json())