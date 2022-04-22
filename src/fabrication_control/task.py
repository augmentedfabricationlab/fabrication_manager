from threading import Thread

__all__ = [
    "Task"
]


class Task():
    def __init__(self):
        self.key = None
        self.is_completed = False
        self.is_running = False
        self._stop_flag = True
        self.log_messages = []

    @property
    def data(self):
        return {
            'key': self.key,
            'is_completed': self.is_completed,
            'is_running': self.is_running,
            '_stop_flag': self._stop_flag,
        }

    @data.setter
    def data(self, data):
        self.key = data['key']
        self.is_completed = data['is_completed']
        self.is_running = data['is_running']
        self._stop_flag = data['_stop_flag']

    @classmethod
    def from_data(cls, data):
        obj = cls()
        obj.data = data

    def perform(self, _stop_flag):
        self._stop_flag = _stop_flag
        if not self.is_running and not self.is_completed:
            self.log("---STARTING TASK---")
            self.t = Thread(target=self.run,
                            args=(lambda: self._stop_flag,))
            self.t.daemon = True
            self.t.start()
            self.is_running = True
        else:
            if self.t.is_alive():
                return False
            else:
                self.t.join()
                del self.t
                self.log("---COMPLETED TASK---")
                self.is_running = False
        if self.is_completed:
            return True

    def run(self, _stop_flag):
        """This method is specific to the type of task"""
        # do something
        finished = True
        if finished:
            self.is_completed = True

    def stop(self):
        self._stop_flag = True
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
    task.perform()
    time.sleep(1)
    print(task.is_completed)
