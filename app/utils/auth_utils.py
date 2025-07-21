from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from functools import wraps
from werkzeug.exceptions import Forbidden

def perfil_required(perfis):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            identidade = get_jwt_identity()
            if identidade['perfil'] not in perfis:
                raise Forbidden('Acesso negado para seu perfil.')
            return fn(*args, **kwargs)
        return wrapper
    return decorator