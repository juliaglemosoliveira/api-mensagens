from models.mensagens import Mensagem
from .. import ma
from marshmallow import fields, validate

class MensagemSchemaEntrada(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Mensagem
        load_instance = True
        exclude = ('id','autor','data_criacao')
    titulo = fields.Str(required=True, validate=validate.Length(max=50))
    conteudo = fields.Str(required=True, validate=validate.Length(max=200))

class MensagemSchemaSaida(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Mensagem
        load_instance = False
        include_fk = True
