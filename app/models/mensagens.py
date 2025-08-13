from app import db
from datetime import datetime
from app.utils.utils import converter_fuso

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    titulo = db.Column(db.String(50), nullable=False)
    conteudo = db.Column(db.String(200), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    autor = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, default=1)

    comentarios = db.relationship('Comentario', backref='mensagens', lazy='select', cascade='all, delete-orphan')

    def json(self, tz_cliente='America/Sao_Paulo'):
        return {
            "id": self.id,
            "titulo":self.titulo,
            "conteudo": self.conteudo,
            "data_hora":converter_fuso(self.data_hora, tz_cliente).isoformat(),
            "autor": self.autor,
            "comentario": [comentario.json() for comentario in self.comentarios]}