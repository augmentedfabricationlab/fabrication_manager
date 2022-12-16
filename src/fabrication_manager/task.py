from threading import Thread

__all__ = [
    "Task"
]


class Task(object):
    def __init__(self, key=None):
        self.key = key
        self.parallelizable = False
        self.is_completed = False
        self.is_running = False
        self.stop_thread = False
        self.log_messages = []

    def __repr__(self):
        return 'Task(key = {self.key}, is_completed={self.is_completed}'
        
    def perform(self, stop_thread):
        self.stop_thread = stop_thread()
        if not self.is_running and not self.is_completed:
            self.is_running = True
            self.log("---STARTING TASK---")
            self.t = Thread(target=self.run,
                            args=(lambda: self.stop_thread,))
            self.t.daemon = True
            self.t.start()
        else:
            if self.t.is_alive():
                return False
            else:
                self.t.join()
                del self.t
                self.is_running = False
                if not self.stop_thread:
                    self.log("---COMPLETED TASK---")
                    return True

    def run(self, stop_thread):
        """This method is specific to the type of task
        Fill your code here for the type of action you want performed"""
        # do something
        finished = True
        if finished:
            self.is_completed = True

    def stop(self):
        self.stop_thread = True
        if hasattr(self, "t"):
            self.t.join()
            del self.t

    def reset(self):
        self.stop()
        self.is_completed = False
        self.is_running = False

    def log(self, msg):
        if isinstance(msg, list):
            for m in msg:
                self.log(m)
        elif str(msg) not in self.log_messages:
            self.log_messages.append("TASK_{}: ".format(self.key) + str(msg))


if __name__ == '__main__':
    import time
    task = Task()
    print(task.is_completed)
    task.perform(False)
    time.sleep(1)
    print(task.is_completed)
