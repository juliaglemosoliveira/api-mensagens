class config:
    #Banco de dados
    SECRET_KEY = 'mensagens'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///dados.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    #Tokens JWT
    JWT_SECRET_KEY = 'chave_secreta'
    JWT_ACCESS_TOKEN_EXPIRES = 3600
    JWT_REFRESH_TOKEN_EXPIRES = 604800 
