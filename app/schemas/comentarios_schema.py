from models.comentarios import Comentario
from .. import ma
from marshmallow import fields, validate

class ComentarioSchemaEntrada(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Comentario
        load_instance = True
        exclude = ('id', 'autor', 'mensagm_id', 'data_criacao')
    
    conteudo = fields.Str(required=True, validate=validate.Length(max=200))

class ComentarioSchemaSaida(ma.SQLAlchemyAutoSchema):
    class Meta():
        model = Comentario
        load_instance = False
        include_fk = True




