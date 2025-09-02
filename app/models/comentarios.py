from app import db
from datetime import datetime
from app.utils.utils import converter_fuso

class Comentario(db.Model):
    __tablename__ = 'comentarios'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    conteudo = db.Column(db.String(200), nullable=False)
    autor = db.Column(db.Integer, db.ForeignKey('usuarios.id'), default=1, nullable=False)
    mensagem_id = db.Column(db.Integer, db.ForeignKey('mensagens.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def json(self, tz_cliente='America/Sao_Paulo'):
      return {'id':self.id,   
             'conteudo':self.conteudo,
               'autor':self.autor,
               'mensagem_id':self.mensagem_id,
               'data_criacao': converter_fuso(self.data_criacao, tz_cliente).isoformat()}