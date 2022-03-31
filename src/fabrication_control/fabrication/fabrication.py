from threading import Thread

__all__ = [
    "Fabrication"
]


class Fabrication(object):
    def __init__(self):
        self.tasks = {}
        self._stop_thread = False
        self.current_task = None

    def add_task(self, task, key=None):
        if key is None:
            key = len(self.tasks)
        self.tasks[key] = task

    def set_tasks(self, tasks):
        for task in tasks:
            self.add_task(task)

    def tasks_available(self):
        if len(self.tasks):
            for task in self.tasks.values():
                if not task.is_completed:
                    return True
            else:
                return False
        return False

    def get_next_task(self):
        keys = [key for key in self.tasks.keys()]
        keys.sort()
        for key in keys:
            task = self.tasks[key]
            if not task.is_completed:
                return task
        else:
            # No next task available
            return None

    def clear_tasks(self):
        self.tasks = {}

    def stop(self):
        self.close()

    def close(self):
        self._join_threads()

    def _join_threads(self):
        self._stop_thread = True
        if hasattr(self, "task_thread"):
            self.task_thread.join()
            del self.task_thread

    def _create_threads(self):
        self._stop_thread = False
        self.task_thread = Thread(target=self.run,
                                  args=(lambda: self._stop_thread,))
        self.task_thread.daemon = True

    def start(self):
        self._join_threads()
        if self.tasks_available():
            self._create_threads()
            self.task_thread.start()
            print("Started task thread")
        else:
            print("No_tasks_available")
    
    def reset(self):
        self.stop()
        for task in self.tasks.values():
            task.reset()
        self.current_task = None

    def run(self, stop_thread):
        self.current_task = self.get_next_task()
        while self.tasks_available():
            if stop_thread():
                break
            elif self.current_task is None or self.current_task.is_completed:
                self.current_task = self.get_next_task()
            elif not self.current_task.is_completed:
                self.current_task.perform()
        else:
            self.log("ALL TASKS DONE")
            self.log("STOPPING FABRICATION")

    def log(self, msg):
        self.log_messages.append("FABRICATION: " + str(msg))
        if len(self.log_messages) > self.log_messages_length:
            self.log_messages = self.log_messages[-self.log_messages_length:] 


if __name__ == '__main__':
    from .task import Task
    import time

    fab = Fabrication()

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
