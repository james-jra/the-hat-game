import os
import logging

logger = logging.getLogger()


def get_secret_key():
    secret_key_env_var = os.environ.get("SECRET_KEY")
    if secret_key_env_var is None:
        logger.warn("No SECRET_KEY environment variable provided")
        return "not-very-secret-default"
    else:
        return secret_key_env_var


class Config(object):
    SECRET_KEY = get_secret_key()
