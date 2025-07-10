from flask import Blueprint, jsonify, request
from app.models.mensagens import Mensagem
from app import db

msg_bp = Blueprint('mensagens', __name__)

#Endpoint para READ - ALL
@msg_bp.route('/mensagens', methods=['GET'])
def read_all():
    mensagens = Mensagem.query.all()
    return jsonify([mensagem.json() for mensagem in mensagens]), 200

#Endpoint para READ ONE
@msg_bp.route('/mensagens/<int:id>', methods=['GET'])
def read_one(id):
    #Verifica se a mensagem existe
    mensagem = Mensagem.query.get(id)
    #Caso ela exista, retorna um json
    if mensagem:
        return jsonify(mensagem.json()), 200
    #Cas onão existe retorna um erro tratado
    return {"Mensagem":"Mensagem não encontrada, tente outro ID!"}, 404

#Endpoint para CREATE
@msg_bp.route('/mensagens', methods=['POST'])
def create_mensagem():
    #Json enviado pelo cliente
    data = request.get_json()

    #Tranforma as chaves da requisição enviada pelo cliente em minusculas, evitando conflitos.
    data_formatada = {chave.lower(): valor for chave, valor in data.items()}

    
    if 'nome' not in data_formatada or "mensagem" not in data_formatada:
        return {"Mensagem":"O campo deve ter obrigatoriamente os campos de 'nome' e 'mensagem' preenchidos adequadamente!"}, 400

    nova_mensagem = Mensagem(nome=data_formatada['nome'], mensagem=data_formatada['mensagem'])
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
    
    return {"Mensagem":"Mensagem não encontrada, tente outro ID!"}, 404

#Endpoint para UPDATE
@msg_bp.route('/mensagens/<int:id>', methods=['PUT'])
def upadte_msg(id):
    mensagem = Mensagem.query.get(id)
    data = request.get_json()
    if not data:
        return jsonify({"Mensagem":"Os dados enviados devem estar no formato adequado(JSON)"})
    
     # Bloqueia alteração do usuário/autor
    if 'usuario' in data:
        return jsonify({"Mensagem": "Não é permitido alterar o autor de uma mensagem."}), 400

    if mensagem:
        mensagem.nome = data.get('nome', mensagem.nome)
        mensagem.mensagem = data.get('mensagem', mensagem.mensagem)

        db.session.commit()
        return jsonify(mensagem.json()), 200
    return jsonify({"Mensagem":"Mensagem não encontrada, tente outro ID!"}), 404

