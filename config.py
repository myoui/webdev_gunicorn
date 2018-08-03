import os
basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_DIR = "app/static/files"
ALLOWED_EXTENSIONS = set(['txt', 'jpg', 'png', 'gif', 'pdf', 'epub', 'mp3'])

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = UPLOAD_DIR
    MAX_CONTENT_LENGTH = 10 * 1024 * 1024
