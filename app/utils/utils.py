import pytz

def converter_fuso(data_hora, tz_cliente='America/Sao_Paulo'):
    if data_hora is None:
        return None
    
    if tz_cliente not in pytz.all_timezones:
        return {'Fuso horário inválido!': tz_cliente}, 400
    
    if data_hora.tzinfo is None:
        data_hora = pytz.utc.localize(data_hora)

    fuso_cliente = pytz.timezone(tz_cliente)
    conversao = data_hora.astimezone(fuso_cliente)
    return conversao

import re
from marshmallow import ValidationError

#Validar e-mail
def validar_email(email):   
    if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
        raise ValidationError ("E-MAIL INVÁLIDO! O E-mail precisa ser, por exemplo: email@dominio.com")
    return email

#Validar senha
def validar_senha(senha):
    #if not re.match(r'^[A-Za-z0-9@!%*?&]+$', senha):
     #   raise ValidationError("SENHA INVÁLIDA! A senha só pode conter esses caracteres: A-Z, a-z, 0-9, @!%*?&")
    if len(senha) < 6:
        raise ValidationError('A senha precisa ser mais do que 8 caracteres')
    if not re.search(r'[0-9]', senha):
        raise ValidationError('A senha precisa conter pelo menos um número')
    if not re.search(r'[A-Z]', senha):
        raise ValidationError('A senha precisa conter pelo menos uma letra maiúsucla!')
    if not re.search(r'[a-z]', senha):
        raise ValidationError('A senha precisa conter pelo menos uma letra minúsucla.')
    if not re.search(r'[@!%*?&]', senha):
        raise ValidationError('A senha precisa conter pelo menos um desses caracteres especiais: @!%*?&')
    return senha