from threading import Thread
from fabrication_manager.utilities import nullcontext
from fabrication_manager.communication import TCPFeedbackServer

__all__ = [
    "FabricationManager"
]


class FabricationManager(object):
    def __init__(self, server_address=(None, None)):
        # General
        self.tasks = {}
        self._stop_thread = True
        self.current_task = None
        self.current_task_key = None
        self.log_messages = []

        # Parallelization functionality
        self.parallelize = False
        self.max_parallel_tasks = 10
        self.running_tasks = []

        # Feedback functionality
        # Example address = ("192.168.0.250", 50005)
        self.server_address = server_address

    def add_task(self, task, key=None):
        # Type of task is of type "Task" or inherited from (only defined in the task itself)
        # FIX: If key was not defined but already exists it will overwrite
        if key is None:
            key = len(self.tasks)
        task.key = key
        self.tasks[key] = task

    def set_tasks(self, tasks):
        for task in tasks:
            self.add_task(task, key=task.key)

    def tasks_available(self):
        if len(self.tasks):
            for task in self.tasks.values():
                if not task.is_completed:
                    return True
                elif task.is_completed and task.is_running:
                    return True
            else:
                return False
        return False

    def get_next_task(self):
        keys = [key for key in self.tasks.keys()]
        keys.sort()
        for key in keys:
            task = self.tasks[key]
            if not task.is_completed and not task.is_running:
                self.current_task_key = key
                return task
        else:
            # No next task available
            return None
        
    def get_next_task_key(self):
        keys = [key for key in self.tasks.keys()]
        keys.sort()
        next_key = keys[-1] + 1
        return next_key
    
    def get_task_by_key(self, key):
        return self.tasks.get(key)

    def clear_tasks(self):
        self.tasks = {}

    def stop(self):
        self.close()
        self.log("FABRICATION: Stopped and joined all threads")

    def close(self):
        self._join_threads()

    def _join_threads(self):
        self._stop_thread = True
        if hasattr(self, "fab_thread"):
            self.fab_thread.join()
            del self.fab_thread

    def _create_threads(self):
        self._stop_thread = False
        self.fab_thread = Thread(target=self.run,
                                 args=(lambda: self._stop_thread,))
        self.fab_thread.daemon = True

    def start(self):
        self._join_threads()
        if self.tasks_available():
            self._create_threads()
            self.fab_thread.start()
            self.log("FABRICATION: Started task thread")
        else:
            self.log("FABRICATION: No tasks available")

    def reset(self):
        self.stop()
        for task in self.tasks.values():
            task.reset()
        self.current_task = None
        self.current_task_key = None
        self.clear_log()
        self.log("FABRICATION: Done resetting all tasks")

    def run(self, stop_thread):
        self.current_task = None
        self.log_messages = []
        self.log("FABRICATION: ---STARTING FABRICATION---")
        if self.server_address[0] is not None:
            self.log(self.server_address)
            with TCPFeedbackServer(*self.server_address) as server:
                self.loop(stop_thread, server)
        else:
            self.loop(stop_thread)

    def loop(self, stop_thread, server=None):            
        get_next_task = False    
        while self.tasks_available():
            if stop_thread():
                self.log("FABRICATION: ---FORCED STOP---")
                break
            
            if self.get_next_task() is not None:
                if self.current_task is None:
                    get_next_task = True
                elif self.parallelize:
                    if (self.current_task.is_running
                            and self.current_task.parallelizable
                            and len(self.running_tasks) < self.max_parallel_tasks):
                        get_next_task = True
                elif not self.parallelize:
                    if (self.current_task.is_completed
                            and not self.current_task.is_running):
                        get_next_task = True
            
            if get_next_task:
                print("Getting new task")
                self.current_task = self.get_next_task()
                get_next_task = False 
                if hasattr(self.current_task, "server"):
                    self.current_task.server = server        

            if len(self.running_tasks) > 0:
                for task in self.running_tasks:
                    task.perform(stop_thread)
                    self.log(task.log_messages)
                    if task.is_completed and not task.is_running:
                        self.running_tasks.remove(task)

            if (not self.current_task.is_completed
                and not self.current_task.is_running
                and self.current_task not in self.running_tasks):
                print("Initializing task")
                self.current_task.perform(stop_thread)
                self.running_tasks.append(self.current_task)
                self.log(self.current_task.log_messages)
        else:
            self.log("FABRICATION: All tasks done")
            self.log("FABRICATION: ---STOPPING FABRICATION---")
        return True

    def log(self, msg):
        if isinstance(msg, list):
            for m in msg:
                self.log(m)
        elif str(msg) not in self.log_messages:
            self.log_messages.append(str(msg))
        # if len(self.log_messages) > self.log_messages_length:
        #     self.log_messages = self.log_messages[-self.log_messages_length:]

    def clear_log(self):
        self.log_messages= []


if __name__ == '__main__':
    from fabrication_manager.task import Task
    import time

    fab = FabricationManager(server_address=("192.168.0.250", 50006))

    tasks = [
        Task(),
        Task(),
        Task(),
    ]

    [fab.add_task(task) for task in tasks]
    print(fab.tasks)
    print([task.is_completed for task in fab.tasks.values()])
    fab.start()
    time.sleep(1)
    fab.stop()
    print([task.is_completed for task in fab.tasks.values()])
