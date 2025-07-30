from app import db
from datetime import datetime
from app.utils.utils import converter_fuso

class Token(db.Model):
    __tablename__ = 'tokens'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    jti = db.Column(db.String(512), nullable=False, unique=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    data_hora = db.Column(db.DateTime, default=datetime.utcnow)
    valido = db.Column(db.Boolean, default=True)

    autor = db.relationship('Usuario', backref='tokens', lazy='select')

    def json(self, tz_cliente='America/Sao_Paulo'):
        return{
            'id':self.id,
            'jti':self.jti,
            'usuario_id':self.usuario_id,
            'data_hora':converter_fuso(self.data_hora, tz_cliente)}