from app import db

class Comentario(db.Model):
    id = db.Column(db.Integer, autoincrement=True)
    comentario = db.Column(db.String(200), nullable=True)
    autor = db.Column(db.Integer, db.ForeignKey('usuarios.id'), default=1)
    mensagem_id = db.Column(db.Integer, db.ForeignKey('mensagens.id'))

    def json(self):
        return {'id':self.id,
                'comentario':self.comentario,
                'autor':self.autor,
                'mensagem_id':self.mensagem_id}
    