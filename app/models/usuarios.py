from app import db

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    nome = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    senha = db.Column(db.String(50))
    perfil = db.Column(db.String(10), default='USER')

    mensagens = db.relationship('Mensagem', backref='usuarios', lazy='select', cascade='all, delete-orphan')
    comentarios = db.relationship('Comentario', backref='usuarios', lazy='select', cascade='all, delete-orphan')
    
    def json(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'perfil': self.perfil}