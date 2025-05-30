from app import db

class Entrada(db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(30), nullable=False)
    mensagem = db.Column(db.String(200))