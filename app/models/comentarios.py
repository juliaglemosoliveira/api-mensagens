from app import db
from datetime import datetime
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
    
class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    comentario = db.Column(db.String(200), nullable=True)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    autor = db.Column(db.Integer, db.ForeignKey('usuarios.id'), default=1)
    mensagem_id = db.Column(db.Integer, db.ForeignKey('mensagens.id'))

    def json(self, tz_cliente='America/Sao_Paulo'):
        return {'id':self.id,   
                'comentario':self.comentario,
                'autor':self.autor,
                'mensagem_id':self.mensagem_id,
                'data_hora': converter_fuso(self.data_hora, tz_cliente)}