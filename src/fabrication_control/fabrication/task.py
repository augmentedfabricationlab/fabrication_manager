from threading import Thread


class Task():
    def __init__(self):
        self.is_completed = False
        self.is_running = False
        self._stop_flag = True

    def perform(self):
        self._stop_flag = False
        if not self.is_running and not self.is_completed:
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
        if self.is_completed:
            return True

    def run(self, _stop_flag):
        """This method is specific to the type of task required to be performed"""
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

if __name__ == '__main__':
    import time
    task = Task()
    print(task.is_completed)
    task.perform()
    time.sleep(1)
    print(task.is_completed)
