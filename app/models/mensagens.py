from app import db

class Mensagem(db.Model):
    __tablename__ = 'mensagens'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(30), nullable=False)
    mensagem = db.Column(db.String(200))
    data_hora = db.Column(db.DateTime)
    autor = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, default=1)

    def json(self):
        return {"id": self.id, "nome": self.nome, "mensagem": self.mensagem, "data_hora":self.data_hora, "autor": self.autor}