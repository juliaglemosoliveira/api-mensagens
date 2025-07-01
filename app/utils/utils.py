import pytz

def converter_fuso(data_hora, tz_cliente='America/Sao_Paulo'):
    if data_hora is None:
        return None
    
    if tz_cliente not in pytz.all_timezones:
        return {'Fuso horário inválido': tz_cliente}, 400
    
    if data_hora.tzinfo is None:
        data_hora = pytz.utc.localize(data_hora)

    fuso_cliente = pytz.timezone(tz_cliente)
    conversao = data_hora.astimezone(fuso_cliente)
    return conversao.strftime('%d-%m-%Y %H:%M')

import re
   
@staticmethod
def validar_email(email):   
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        return {"mensagens":"email inválido"}
    return True
    
@staticmethod
def validar_senha(senha):
    if not re.match(r'^[A-Za-z0-9@!%*?&]+$', senha):
        return {"mensagem":"A senha só pode conter esses caracteres: A-Z, a-z, 0-9, @!%*?&"}
    
    if (len(senha) < 8      or
        not re.search(r'[0-9]', senha) or
        not re.search(r'[A-Z]', senha) or
        not re.search(r'[a-z]', senha) or
        not re.search(r'[@!%*?&]', senha)):
        return {"mensagem":"a Senha deve ser mais que 8 digitos e conter pelo menos um desses caracteres:0-9, A-Z, a-z, @!%*?&"}
       
    return True