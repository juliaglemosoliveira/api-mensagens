from flask import Blueprint, jsonify, request
from app.models.mensagens import Mensagem
from app.models.usuarios import Usuario
from app import db
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden

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
    #Caso ela exista, retorna a mensagem em JSON
    if mensagem:
        return jsonify(mensagem.json()), 200
    #Caso não exista, ele retorna um erro tratado
    raise NotFound("Mensagem não encontrada, tente outro ID!")

#Endpoint para CREATE
@msg_bp.route('/mensagens', methods=['POST'])
def create_mensagem():
    #JSON enviado pelo cliente
    data = request.get_json()
    #Capitaliza as chaves enviadas na requisição, pelo cliente, evitando conflitos
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}
    #Verifica se realmente as chaves estão realmente presentes na requisição, se não estiver, retorna um erro tratado    
    if 'Nome' not in data_formatada or "Mensagem" not in data_formatada:
        raise BadRequest("Os campos'Nome' e 'Mensagem' devem ser preenchidos adequadamente!")
    
    nome = data_formatada.get('Nome')
    mensagem = data_formatada.get('Mensagem')

    if not nome or not mensagem or not nome.strip() or not mensagem.strip():
        raise BadRequest('É obrigatório o preenchimento do nome e comentário.')
    
    #Adiciona os valores enviados na requisição ao banco de dados
    nova_mensagem = Mensagem(nome=data_formatada['Nome'], mensagem=data_formatada['Mensagem'])
    db.session.add(nova_mensagem)
    db.session.commit()
    #Retorna a mensagem que foi adicionada
    return jsonify(nova_mensagem.json()), 201

#Endpoint para DELETE
@msg_bp.route('/mensagens/<int:id>', methods=['DELETE'])
def delete_msg(id):
    #Procura a mensagem de acordo com o ID enviado pelo cliente na URL
    mensagem = Mensagem.query.get(id)
    #Caso essa mensagem existe, ela é excluída do banco de dados
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")
    
    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.captalize():valor for chave, valor in data.items()}

    senha_autor = data_formatada.get('Senha')
    email_autor = data_formatada.get('Email')

    #Verificação: Confere se o usuario que está tentando apagar o usuário é o próprio usuário.
    usuario = Usuario.query.filter_by(email=email_autor, senha=senha_autor).first()
    if None in usuario :
        raise Unauthorized('Senha ou email incorretos, por favor, digite-os valores corretamente.')
    
    if usuario.autor != usuario.id:
        raise Forbidden('Você não tem permissão para apagar essa mensagem!')

    db.session.delete(mensagem)
    db.session.commit()
    #Retorna um confirmação de sucesso para a operação
    return {"Mensagem":"Mensagem excluída com sucesso!"}, 200
    

#Endpoint para UPDATE
@msg_bp.route('/mensagens/<int:id>', methods=['PUT'])
def upadte_msg(id):
    #Procura a mensagem de acordo com ID enviado pelo cliente na URL
    mensagem = Mensagem.query.get(id)
    #Caso não seja encontrado a mensagem, retorna um erro tratado
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")

    #Requisição enviada pelo cliente
    data = request.get_json()
    #Capitaliza as chaves enviadas na requisição, pelo cliente, evitando conflitos
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    #Verifica se realmente as chaves estão realmente presentes na requisição, se não estiver, retorna um erro tratado    
    if 'Mensagem' not in data_formatada or 'Nome' not in data_formatada:
        raise BadRequest("O campo deve ter obrigatoriamente os campos de 'Nome' e 'Mensagem' preenchidos adequadamente!")
    
    # Bloqueia alteração do usuário/autor, caso o cliente tente enviar a troca pela requisição
    if 'Autor' in data_formatada:
        raise BadRequest("Não é permitido alterar o autor de uma mensagem.")
    
    #Se a mensagem realmente existir e estiver nos conformes, ele faz a alteração
    mensagem.nome = data_formatada.get('Nome', mensagem.nome)
    mensagem.mensagem = data_formatada.get('Mensagem', mensagem.mensagem)
    db.session.commit()
    #retorna a mensagem atualizada
    return jsonify(mensagem.json()), 200
    

