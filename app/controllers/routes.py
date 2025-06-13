from flask import Blueprint, jsonify, request
from app.models.caixa_de_entrada import Entrada
from app import db

msg_bp = Blueprint('mensagens', __name__)

#Endpoint para READ - ALL
@msg_bp.route('/mensagens', methods=['GET'])
def read_all():
    mensagens = Entrada.query.all()
    return jsonify([mensagem.json() for mensagem in mensagens])

#Endpoint para CREATE
@msg_bp.route('/mensagens', methods=['POST'])
def create_mensagem():
    data = request.get_json()
    nova_mensagem = Entrada(nome=data['nome'], mensagem=data['mensagem'])
    db.session.add(nova_mensagem)
    db.session.commit()
    return jsonify(nova_mensagem.json()), 201
    

