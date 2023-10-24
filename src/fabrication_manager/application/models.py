from fabrication_manager.application import db
from sqlalchemy.sql import func

class Task(db.Model):
    pyobj = db.Column(db.String(10000))
    id = db.Column(db.Integer, primary_key=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    module= db.Column(db.String(150))
    name= db.Column(db.String(150))
    state = db.Column(db.String(150))
    stop = db.Column(db.Integer)
    data = db.Column(db.JSON)
    children = db.relationship("Task", back_populates="parent")
    parent = db.relationship("Task", back_populates="children", remote_side=[id])

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    ip = db.Column(db.String(150))
    status = db.Column(db.String(150))
    messages = db.relationship('Message')

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    message = db.Column(db.String(1000))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))