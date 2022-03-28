from os import environ, path, urandom
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, ".env"))

UPLOAD_FOLDER = path.join(basedir, "pm_crm/static/uploads")
ALLOWED_EXTENSIONS = {"xls"}
MAX_CONTENT_LENGTH = 1 * 1024 * 1024 / 10

SECRET_KEY = urandom(32)


class Config:
    """Base Config"""

    SECRET_KEY = SECRET_KEY
    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    UPLOADED_DATAFILES_DEST = UPLOAD_FOLDER
    ALLOWED_EXTENSIONS = ALLOWED_EXTENSIONS
    MAX_CONTENT_LENGTH = MAX_CONTENT_LENGTH

    # Database
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class ProdConfig(Config):
    FLASK_ENV = "production"
    DEBUG = False
    TESTING = False
    # DATABASE_URI = environ.get("PROD_DATABASE_URI")


class DevConfig(Config):
    FLASK_ENV = "development"
    DEBUG = True
    TESTING = True
    DATABASE_URI = environ.get("DEV_DATABASE_URI")
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"
