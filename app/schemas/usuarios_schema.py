from models.usuarios import Usuario
from .. import ma
from marshmallow import fields, validate
from utils.utils import validar_email, validar_senha

class UsuarioSchemaEntrada(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Usuario
        load_instance=True
        exclude = ('id')

    email = fields.Str(required=True, validate=[validar_email, validate.Length(max=100)])
    senha = fields.Str(required=True, validate=[validar_senha, validate.Length(max=50)])
    nome = fields.Str(required=True, validate=validate.Length(max=80))
    perfil = fields.Str(required=True, validate=validate.Length(max=10))
    

class UsuarioSchemaSaida(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Usuario
        load_instance = False
        include_fk = True