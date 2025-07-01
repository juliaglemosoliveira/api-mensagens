from app import db
from datetime import datetime
from app.utils.utils import converter_fuso
    
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