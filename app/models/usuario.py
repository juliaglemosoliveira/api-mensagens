from app import db
import re

class Usuario(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), unique=True, nullable=False)
    senha = db.Column(db.String(30))

    db.relationship('Entrada', backref='usuarios', lazy=True )

    def json(self):
        return {"id": self.id, "nome": self.nome, "email": self.email, "senha": self.senha}
    

    def validar_senha(senha):
        if (len(senha) < 8 or
            not re.search(r'[0-9]', senha) or
            not re.search(r'[A-Z]', senha) or
            not re.search(r'[a-z]', senha) or
            not re.search(r'[@!%*?&]', senha)):
            return False
        return True

