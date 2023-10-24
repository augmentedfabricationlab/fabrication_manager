from flask import Flask
from fabrication_manager.application.exts import db, socketio, make_celery

DB_NAME = "database.db"

# Creating the app in Flask, the SQL database, SocketIO implementation, and the Celery distributed system
def create_app():
    # Flask initialization
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "fabrication_manager"
    
    # Setting the database location (currently defaults to the src/instance folder in fabrication_manager)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    
    # Setting Celery backend location
    app.config['CELERY_BROKER_URL'] = 'amqp://localhost'
    app.config['CELERY_RESULT_BACKEND'] = f'db+sqlite:///{DB_NAME}'
    
    # Initilizing the SQLAlchemy database to the app
    db.init_app(app)

    # Initializing SocketIO
    socketio.init_app(app)
    # Initializing Celery
    celery = make_celery(app)

    # Registering routes and html    
    from .views import views
    app.register_blueprint(views, url_prefix='/')

    from .comm import connect, disconnect, message, add_task
    from .tasks import start_fabrication, run_task

    # Importing SQL database models
    from .models import Task, User, Message

    # Creating or opening the database within the app context
    with app.app_context():
        db.create_all()
        db.session.commit()

    return socketio, celery, app