from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(30))

    mensagens = db.relationship('Mensagem', backref='usuarios', lazy='select' )
    comentarios = db.relationship('Comentario', backref='usuarios', lazy='select')

    def json(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "email": self.email,
            "senha": self.senha}
 