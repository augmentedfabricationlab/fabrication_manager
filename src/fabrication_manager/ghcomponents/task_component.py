''' 
------------------------------------------------------
/// The code in the Grasshopper "Create Tasks" component ///
------------------------------------------------------
Component Inputs:
create: Boolean

Component Outputs:
tasks: List[Task]
'''
import time
from fabrication_manager.task import Task

class Task1(Task):
    def work_func(self, results, interrupt_event):
        # do something
        self.log("This is task 1")
        time.sleep(0.5)

class Task2(Task):
    def work_func(self, results, interrupt_event):
        # do something
        self.log("Task 2 counting up")
        for i in range(10):
            self.log("Counting: {}".format(i))
            time.sleep(0.1)

class Task3(Task):
    def work_func(self, results, interrupt_event):
        # do something
        self.log("Task 3 starting...")
        current_time = time.time()
        while time.time()<(current_time+1):
            self.log("waiting...")
        else:
            self.log("done waiting!")

if create:
    task1 = Task(key=0)
    task2 = Task(key=1)
    task3 = Task(key=2)

tasks = [task1, task2, task3]
