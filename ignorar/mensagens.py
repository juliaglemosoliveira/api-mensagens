from flask import Blueprint, jsonify, request
from app.models.mensagens import Mensagem
from app.models.comentarios import Comentario
from app import db
from werkzeug.exceptions import NotFound, BadRequest, Unauthorized, Forbidden
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
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
    if 'Titulo' not in data_formatada or "Conteudo" not in data_formatada:
        raise BadRequest("Os campos'Titulo' e 'Conteudo' devem ser preenchidos adequadamente!")
    
    #Acrescente as informações da rquisição as suas respectivas variáveis
    titulo = data_formatada.get('Titulo')
    conteudo = data_formatada.get('Conteudo')

    #Vericia se os campos Nome e Mensagem estão preenchidos adequadamente
    if not titulo or not conteudo or not titulo.strip() or not conteudo.strip():
        raise BadRequest('É obrigatório o preenchimento do nome e comentário.')
    
    #Verifica quem está autenticado
    identidade = get_jwt_identity()
    
    #Adiciona os valores enviados na requisição ao banco de dados
    nova_mensagem = Mensagem(titulo=data_formatada['Titulo'], conteudo=data_formatada['Conteudo'], autor=identidade)
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

    # Bloqueia alteração do usuário/autor, caso o cliente tente enviar a troca pela requisição
    if 'Autor' in data_formatada:
        raise BadRequest("Não é permitido alterar o autor de uma mensagem.")
    
    identidade = get_jwt_identity()
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and mensagem.autor != int(identidade):
        raise Forbidden('Você não tem autorização para alterar essa mensagem!')

    #Atualiza as informações no banco de dados(caso não haja dados na requisição, permanece os valores que já estavam)
    mensagem.titulo = data_formatada.get('Titulo', mensagem.titulo)
    mensagem.conteudo = data_formatada.get('Conteudo', mensagem.conteudo)
    db.session.commit()
    #retorna a mensagem atualizada
    return jsonify(mensagem.json()), 200

#Endpoint para UPDATE PARCIAL
@msg_bp.route('/<int:id>', methods=['PATCH'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def modificar_mensagem(id):

    #Procura a mensagem de acordo com ID enviado pelo cliente na URL
    mensagem = Mensagem.query.get(id)
    #Caso não seja encontrado a mensagem, retorna um erro tratado
    if not mensagem:
        raise NotFound("Mensagem não encontrada, tente outro ID!")

    #Requisição enviada pelo cliente
    data = request.get_json()

    #Capitaliza as chaves enviadas na requisição, pelo cliente, evitando conflitos
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    # Bloqueia alteração do usuário/autor, caso o cliente tente enviar a troca pela requisição
    if 'Autor' in data_formatada or 'Titulo' in data_formatada:
        raise BadRequest("Não é permitido alterar o autor ou titulo de uma mensagem por esse método.")
    
    identidade = get_jwt_identity()
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and mensagem.autor != int(identidade):
        raise Forbidden('Você não tem autorização para alterar essa mensagem!')

    #Atualiza as informações no banco de dados(caso não haja dados na requisição, permanece os valores que já estavam)
    mensagem.titulo = data_formatada.get('Titulo', mensagem.titulo)
    mensagem.conteudo = data_formatada.get('Conteudo', mensagem.conteudo)
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
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and mensagem.autor != int(identidade):
        raise Forbidden('Você não tem permissão para apagar essa mensagem!')

    db.session.delete(mensagem)
    db.session.commit()
    #Retorna um confirmação de sucesso para a operação
    return {"Mensagem":"Mensagem excluída com sucesso!"}, 200

#Endpoint para Comentario por Mensagem
@msg_bp.route('/<int:mensagem_id>/comentarios', methods=['GET'])
def comentarios_por_mensagem(mensagem_id):
    #Busca por um comentário específico, com base no ID da mensagem informado na URL
    comentarios = Comentario.query.filter_by(mensagem_id=mensagem_id).all()
    if not comentarios:
        raise NotFound('Não existe nenhum comentário para essa mensagem.')
    #Retorna todos os comentários que existem para aquela mensagem no formato JSON
    return jsonify([comentario.json() for comentario in comentarios]), 200

# Endpoint para CREATE
@msg_bp.route('/<int:mensagem_id>/comentarios', methods=['POST'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def criar_comentario(mensagem_id):
    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.capitalize(): valor for chave, valor in data.items()}

    # Verificando se os dados obrigatórios estão na requisição enviada
    if 'Conteudo' not in data_formatada:
        raise BadRequest("O campo de 'Conteudo' deve ser preenchido adequadamente!")

    #Acrescente as informações da requisição as suas respectivas variáveis
    conteudo = data_formatada.get('Conteudo')

    # Verifica se a mensagem para qual o comentário é destinado realmente exite
    mensagem = Mensagem.query.get(mensagem_id)
    if not mensagem:
        raise NotFound('Nenhuma mensagem com esse ID, tente outro!')

    identidade = get_jwt_identity()
    
    #Adição do novo comentário ao banco de dados
    novo_comentario = Comentario(conteudo=conteudo,mensagem_id=mensagem_id, autor=identidade)
    db.session.add(novo_comentario)
    db.session.commit()
    #Retorna o comentário criado para o cliente
    return jsonify(novo_comentario.json()), 201


# Endpoint para UPDATE
@msg_bp.route('/<int:mensagem_id>/comentarios/<int:comentario_id>', methods=['PUT'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def atualizar_comentario(mensagem_id, comentario_id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.filter_by(mensagem_id=mensagem_id, id=comentario_id).first()
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')

    #Requisição enviada pelo cliente
    data = request.get_json()

    #Formatando as chaves para que estejam devidamente capitalizadas, evitando erros
    data_formatada = {chave.capitalize():valor for chave, valor in data.items()}

    #Verifica se Comentario está na requsição enviada
    if 'Conteudo' not in data_formatada:
        raise BadRequest("O campo 'Conteudo' deve ser preenchido adequadamente")

     # Bloqueia alteração de autor e mensagem_id
    if 'Autor' in data or 'Mensagem_id' in data:
        raise BadRequest('Não é permitido alterar o autor ou mensagem_id de um comentário.')
    
    identidade = get_jwt_identity()
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and comentario.autor != int(identidade):
        raise Forbidden('Você não tem autorização para alterar esse comentário!')
    
     #Atualiza as informações no banco de dados(caso não haja dados na requisição, permanece os valores que já estavam)
    comentario.conteudo = data_formatada.get('Conteudo', comentario.conteudo)
    db.session.commit()
    return jsonify(comentario.json()), 200

# Endpoint para DELETE
@msg_bp.route('/<int:mensagem_id>/comentarios/<int:comentario_id>', methods=['DELETE'])
@jwt_required()
@perfil_required(['ADMIN', 'USER'])
def deletar_comentario(mensagem_id, comentario_id):
    #Busca por um comentário específico, com base no ID informado na URL
    comentario = Comentario.query.filter_by(mensagem_id=mensagem_id, id=comentario_id).first()
    if not comentario:
        raise NotFound('Nenhum comentário com esse ID, tente outro!')
    
    identidade = get_jwt_identity()
    claims = get_jwt()
    perfil = claims.get('perfil')

    if perfil != 'ADMIN' and comentario.autor != int(identidade):
        raise Forbidden('Você não tem autorização para deletar esse comentário!')
   
    #Delete o comentário do banco de dados, caso todos os requisitos sejam atendidos
    db.session.delete(comentario)
    db.session.commit()
    return jsonify({'Mensagem': 'Comentário deletado com sucesso!'}), 200

    