import os


basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
# SQLite local
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'sghss.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret')