from fabrication_manager.application import create_app

socketio, celery, app = create_app()

if __name__ == "__main__":
    celery = celery
    socketio.run(app=app, debug=True)

