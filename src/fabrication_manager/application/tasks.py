from flask import jsonify
from flask_socketio import emit
from celery import shared_task
from fabrication_manager.application.exts import db
from fabrication_manager.application.models import Task
import jsonpickle

def import_class(module, name):
    mods = module.split('.')
    cls = __import__(mods[0])
    for mod in mods[1:]:
        cls = getattr(cls, mod)
    return getattr(cls, name)

@shared_task
def stop_fabrication():
    pass

@shared_task
def run_task(task):
    taskobj = jsonpickle.decode(task)
    taskobj.run()

@shared_task
def start_fabrication():
    tasks = db.session.query(Task).filter(Task.state != "SUCCES")
    print(tasks)
    for task in tasks:
        # task_cls = import_class(task.module, task.name)
        result = run_task.delay(task.pyobj)
        task.state = "STARTED"
        db.session.commit()
        # emit("message", f"Started Task {task.id}...", namespace='/', broadcast=True)
        print(result)
        result.get()
        task.state = "SUCCESS"
        db.session.commit()
        emit("message", f"Finished Task {task.id}!", namespace='/', broadcast=True)
    
