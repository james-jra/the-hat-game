__version__ = '0.1.0'
from config import Config
from flask import Flask
from flask_bootstrap import Bootstrap
import logging
from logging.handlers import RotatingFileHandler
import os

app = Flask(__name__)
app.config.from_object(Config)

# Link up the other bits of the app
from hat_game import routes, errors # noqa

# Init extensions
bootstrap = Bootstrap(app)

# Set-up app logger
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/hat-game.log', maxBytes=10240,
                                       backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Hat game startup')
