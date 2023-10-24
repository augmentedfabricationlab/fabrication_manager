from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from celery import Celery

db = SQLAlchemy()
socketio = SocketIO(async_mode=None)

# Setting up the Celery distributed system
def make_celery(app):
    celery = Celery(main=app.import_name, backend=app.config['CELERY_RESULT_BACKEND'],
                    broker=app.config['CELERY_BROKER_URL'])
    return celery