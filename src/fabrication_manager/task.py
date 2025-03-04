import time
from multiprocessing import Process

__all__ = [
    "Task"
]

class Task(object):
    def __init__(self, key=None, parallelizable=False):
        self.key = key
        self.process = None
        self.parallelizable = parallelizable
        self.is_completed = False
        self.is_running = False
        self.log_messages = []

    def __repr__(self):
       return type(self).__name__
        
    def _run(self, results, interrupt_event):
        """
        Internal wrapper that runs the work function.
        Because the work_func might be fully blocking, it does not check
        the interrupt_event. If interrupt_event is set, we simply rely on the
        process being terminated externally.
        """
        results.put(f"Task {self.key} started")
        self.is_running = True
        try:
            self.work_func(results, interrupt_event)
        except Exception as e:
            results.put(f"Task {self.key} encountered error: {e}")
        # If we were not interrupted (i.e. process not terminated), mark as completed.
        if not interrupt_event.is_set():
            results.put(f"Task {self.key} completed")
            self.is_completed = True
        else:
            results.put(f"Task {self.key} interrupted")
            self.is_completed = False

    def work_func(self, results, interrupt_event):
        """This is the function that should be overridden by subclasses."""
        for i in range(4):
            if interrupt_event.is_set():
                return
            time.sleep(0.5)  # blocking sleep to simulate work
            results.put(f"Task {self.key} step {i}...")

    def start(self, results, interrupt_event):
        """Starts the task in its own process if it hasn't been started already."""
        if self.process is None:
            self.process = Process(target=self._run, args=(results, interrupt_event))
            self.process.start()
            self.is_running = True

    def join(self):
        """Wait for the task's process to complete."""
        if self.process:
            self.process.join()
            self.is_running = False
            self.process = None         

    def terminate(self):
        """Forcefully stop the task's process."""
        if self.process:
            self.process.terminate()
            self.is_completed = False
            self.is_running = False

    def reset(self):
        """Reset the task to its initial state."""
        self.is_completed = False
        self.is_running = False
        self.log_messages = []

    def log(self, msg):
        if isinstance(msg, list):
            for m in msg:
                self.log(m)
        elif str(msg) not in self.log_messages:
            self.log_messages.append("TASK_{}: ".format(self.key) + str(msg))


if __name__ == '__main__':
    from multiprocessing import Queue, Event
    
    logs = []
    results = Queue()
    interrupt_event = Event()

    task = Task(key = 0)
    print(task.is_completed)
    
    task.start(results, interrupt_event)
    print("Task started.")
    task.join()
    print("Task joined.")

    while True:
        try:
            msg = results.get_nowait()
            print("LOG:", msg)
            logs.append(msg)
        except Exception:
            break
