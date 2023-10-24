from flask import Blueprint, render_template, request, flash, jsonify

from fabrication_manager.application.exts import db
from fabrication_manager.application.models import Task, User, Message
from fabrication_manager.application.tasks import start_fabrication

import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        start = request.form.get('start')
        stop = request.form.get('stop')
        reset = request.form.get('reset')
        clear = request.form.get('clear')
        print({"start":start, "stop":stop, "reset": reset,"clear":clear})
        if start:
            start_fabrication()
            flash('Starting fabrication', category='succes')
        if stop:
            flash('Stopping fabrication', category='error')
        if reset:
            flash('Resetting fabrication', category='succes')
        if clear:
            flash('Cleared all tasks', category='succes')

    return render_template("home.html")

@views.route('/tasks-view', methods=['GET','POST'])
def tasks_view():
    return render_template("tasks-view.html", tasks=db.session.query(Task))

@views.route('/delete-task', methods=['POST'])
def delete_task():
    task = json.loads(request.data)
    taskId = task['taskId']
    task = Task.query.get(taskId)
    if task:
        db.session.delete(task)
        db.session.commit()
    return jsonify({})

@views.route('/clients')
def clients_view():
    return render_template("clients.html", data=db.session.query(User))

@views.route('/logs')
def logs_view():
    return render_template("logs.html", messages=db.session.query(Message))

def get_class(module, class_name):
    components = module.split('.')
    components.append(class_name)
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod