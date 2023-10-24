import jsonpickle
from socketio import Client
from fabrication_manager import Task

client = Client()

@client.event
def connect():
    print("Connected")

@client.event
def disconnect():
    print("Disconnected!")


class AddTask(Task):
    def __init__(self, id, num1, num2, parent_id=None):
        super().__init__(id, parent_id)
        self.task_data = {
            "num1": num1,
            "num2": num2,
            "result": None
        }

    def run(self):
        self.task_data["result"] = self.task_data.get("num1")+self.task_data.get("num2")

if __name__ == "__main__":
    client.connect("http://localhost:5000")
    client.emit("message", "Adding tasks to database")
    from fabrication_manager.application.test_connection import AddTask
    for i in range(5):
        if i == 0:
            task = AddTask(id=i, num1=i+1, num2=i*2)
        else:
            task = AddTask(id=i, parent_id=i-1, num1=i+1, num2=i*2)
        client.emit("add_task", task.data)

    client.emit("message", "Finished adding tasks!")

    # task = Task(key=0)
    # client.emit("add_task", task.data())
    # def my_import(module, name):
    #     components = module.split('.')
    #     components.append(name)
    #     mod = __import__(components[0])
    #     for comp in components[1:]:
    #         mod = getattr(mod, comp)
    #     return mod
    
    # mod = str(type(task).__module__)
    # kla = str(type(task).__name__)
    # klass = my_import(mod, kla)

    # new_task2 = klass(key=2)
    # print(new_task2.key)

    import time
    time.sleep(1)
    client.disconnect()