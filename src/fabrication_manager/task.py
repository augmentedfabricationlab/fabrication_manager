# import jsonpickle
from threading import Thread
from compas.data import Data

__all__ = [
    "Task"
]


class Task():
    def __init__(self, id, parent_id=None):
        self.id = id
        self.parent_id = parent_id
        self.__module__ = str(type(self).__module__)
        self.__name__ = str(type(self).__name__)
        self.state = "PENDING" # PENDING, STARTED, RETRY, FAILURE, SUCCESS
        self.stop = False
        self.task_data = {}
        self.log_messages = []

    @property
    def data(self):
        return {
            "id": self.id,
            "parent_id": self.parent_id,
            "__module__": self.__module__,
            "__name__": self.__name__,
            "state": self.state,
            "stop": self.stop,
            "task_data": self.task_data,
            "pyobj": jsonpickle.encode(self)
        }

    def __repr__(self):
       return "Task_{}_complete".format(self.id)

    def run(self, stop):
        """This method is specific to the type of task
        Fill your code here for the type of action you want performed"""
        # do something
        finished = True
        if finished:
            self.state = "completed"
        self.log("Completed")

    def stop_task(self):
        self.stop = True

    def reset(self):
        self.stop_task()
        if self.state in ["initialized", "waiting", "running", "completed"]:
            self.state == "initialized"
        elif self.state in ["defined", "undefined"]:
            pass

    def log(self, msg):
        if isinstance(msg, list):
            for m in msg:
                self.log(m)
        elif str(msg) not in self.log_messages:
            self.log_messages.append("TASK_{}: ".format(self.key) + str(msg))


if __name__ == '__main__':
    # import time
    # task = Task()
    # print(task.is_completed)
    # task.perform(False)
    # time.sleep(1)
    # print(task.is_completed)
    from fabrication_manager import Task
    task = Task(0)
    import jsonpickle

    frz = jsonpickle.encode(task)
    print(frz)

