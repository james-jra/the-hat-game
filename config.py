import os
import logging

basedir = os.path.abspath(os.path.dirname(__file__))
logger = logging.getLogger()


def get_secret_key():
    secret_key_env_var = os.environ.get("SECRET_KEY")
    if secret_key_env_var is None:
        logger.warn("No SECRET_KEY environment variable provided")
        return "not-very-secret-default"
    else:
        return secret_key_env_var


def get_db_uri():
    db_uri_env_var = os.environ.get("DATABASE_URL")
    if db_uri_env_var is None:
        logger.warn("No DATABASE_URL environment variable provided")
        db_url = 'sqlite:///' + os.path.join(basedir, 'app.db')
    else:
        db_url = db_uri_env_var

    logger.info("Using database {}".format(db_url))
    return db_url


class Config(object):
    SECRET_KEY = get_secret_key()
    SQLALCHEMY_DATABASE_URI = get_db_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
