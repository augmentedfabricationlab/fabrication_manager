import datetime 
from flask import request, flash, session
from flask_socketio import emit
from fabrication_manager.application.models import User, Message, Task
from fabrication_manager.application.exts import db, socketio

@socketio.on("connect")
def connect(auth):
    exists = db.session.query(
        db.session.query(User).filter(User.ip == str(request.remote_addr)).exists()
    ).scalar()
    if exists is None or exists is False:
        user = User(ip=request.remote_addr, name=request.remote_user, status="Connected")
        db.session.add(user)
        print("new user created")
    else:
        user = db.session.query(User).filter(User.ip == str(request.remote_addr)).first()
        user.status = "Connected"
    
    session['userId'] = user.id
    print(f"user {session['userId']} at {request.remote_addr} connected")
    db.session.commit()
    session["userId"] = user.id

    users = db.session.query(User).filter(User.status == "Connected")
    count = len([u for u in users])
    emit("users", {"user_count": count}, broadcast=True)

@socketio.on("disconnect")
def disconnect():
    userId = session.get("userId")
    user = db.session.query(User).filter(User.id == userId)
    user.status = "Disconnected"
    db.session.commit()
    print(f"User {session['userId']} at {request.remote_addr} DISconnected")
    
    users = db.session.query(User).filter(User.status == "Connected")
    count = len([u for u in users])
    emit("users", {"user_count": count}, broadcast=True)

@socketio.on("message")
def message(data):
    userId = session.get("userId")
    msg = Message(date=datetime.datetime.now(), message=data, user_id=userId)
    db.session.add(msg)
    db.session.commit()

@socketio.on("add_task")
def add_task(json):
    print(f"received: {json}")
    if json.get('id') is None:
        print('Task did not have id defined, was not added')
        return
    task = Task(pyobj=json.get("pyobj"),
                id=json.get("id"),
                parent_id=json.get("parent_id"),
                module=json.get("__module__"),
                name=json.get("__name__"),
                state=json.get("state"),
                stop=json.get("stop"),
                data=json.get("data"))
    db.session.add(task)
    db.session.commit()
    flash('Task created!', category='success')