from flask_jwt_extended import verify_jwt_in_request, get_jwt
from functools import wraps
from werkzeug.exceptions import Forbidden

#Aqui é feita a criação de um decorador para verificação se o Usuário é ADMIN ou USER

#Aqui é passado para a função o parametro perfis, para que o código saiba o que procurar
def perfil_required(perfis):
    #Aqui é criador o decorador
    def decorador(funcao_original):
        #Função usado para garantir a integridade dos dados(Não é obrigatório, mas é bom usá-lo)
        @wraps(funcao_original)
        #O "coração" do decorador, onde é pegado os dados args(dados posicionais) e os kwargs(dados chave:valor)
        def verificador(*args, **kwargs):
            #Verifica a integridade do Token
            verify_jwt_in_request()
            #Decodifica o token e pega os dados de identidade contidos nele
            identidade = get_jwt()
            #Se o perfil do token for inadequado para função X, então é retornado um erro tratado
            if identidade['perfil'] not in perfis:
                raise Forbidden('Acesso negado para seu perfil.')
            #Retorna a função original e seus parametros, para que seja possível serem usados por ela
            return funcao_original(*args, **kwargs)
        #Retorna a lógica do verificador
        return verificador
    #É retornado o decorador, no caso, depois de ter verificado a função decorada
    return decorador