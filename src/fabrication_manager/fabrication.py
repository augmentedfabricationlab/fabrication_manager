import time
# from threading import Thread
from multiprocessing import Process, Queue, Event
# from compas.datastructures import Graph
# from fabrication_manager.utilities import nullcontext
from fabrication_manager.communication import TCPFeedbackServer

__all__ = [
    "FabricationManager"
]


class FabricationManager(object):
    def __init__(self, server_address=(None, None)):
        # General
        self.tasks = {}
        self.log_messages = []

        # Feedback functionality
        # Example address = ("192.168.0.250", 50005)
        self.server_address = server_address

        # Multiprocessing functionality
        self.results = Queue()
        self.interrupt_event = Event()
        self.fab_process = None

        # Parallelization
        self.running_tasks = []
        self.parallelize = True
        self.max_parallel_tasks = 2

    def add_task(self, task, key=None):
        # Type of task is of type "Task" or inherited from (only defined in the task itself)
        # FIX: If key was not defined but already exists it will overwrite
        if key is None:
            key = len(self.tasks)
        task.key = key
        task.is_completed = False
        task.is_running = False
        # If the task doesn't have a parallelizable attribute, default to False.
        if not hasattr(task, 'parallelizable'):
            task.parallelizable = False
        self.tasks[key] = task

    def set_tasks(self, tasks):
        for task in tasks:
            self.add_task(task, key=task.key)

    def tasks_available(self):
        return any(not t.is_completed for t in self.tasks.values())

    def get_next_task(self):
        keys = sorted(self.tasks.keys())
        for key in keys:
            task = self.tasks[key]
            if not task.is_completed and not task.is_running:
                return task
        return None

    def clear_tasks(self):
        self.tasks = {}
    
    def _cleanup(self):
         # Remove finished tasks.
        still_running = []
        for task in self.running_tasks:
            if task.process.is_alive():
                still_running.append(task)
            else:
                task.process.join()
                self.results.put(f"Finished parallel task {task.key}")
        self.running_tasks = still_running

    def _run_tasks(self):
        """
        This method is executed in a separate process.
        It sends log messages via the results Queue and runs tasks one after the other.
        """
        self.results.put("FABRICATION: ---STARTING FABRICATION ---")
        if self.server_address[0] is not None:
            self.results.put("Server address: " + str(self.server_address))
            with TCPFeedbackServer(*self.server_address) as server:
                self._task_loop(server)
        else:
            self._task_loop()
        self.results.put("FABRICATION: ---STOPPING FABRICATION ---")

    def _task_loop(self, server=None):            
         while self.tasks_available():
            self._cleanup()

            if self.interrupt_event.is_set():
                self.results.put("FABRICATION: Interrupted")
                return 
            
            task = self.get_next_task()
            if task is not None and not task.is_running:
                if task.parallelizable and self.parallelize:
                    # Wait if we've reached the max number of parallel tasks.
                    while len(self.running_tasks) >= self.max_parallel_tasks:
                        self._cleanup()
                        time.sleep(0.1)
                    self.results.put(f"Starting parallel task {task.key}")
                    task.start(self.results, self.interrupt_event)
                    self.running_tasks.append(task)
                else:
                    # Before a non-parallelizable task, wait for all parallel tasks.
                    while len(self.running_tasks):
                        self._cleanup()
                        time.sleep(0.1)
                    # self.running_tasks = []
                    self.results.put(f"Starting sequential task {task.key}")
                    task.start(self.results, self.interrupt_event)
                    task.join()
                    self.results.put(f"Finished sequential task {task.key}")
                time.sleep(0.05)

    def start(self):
        self.interrupt_event.clear()
        if self.tasks_available():
            self.fab_process = Process(target=self._run_tasks)
            # self.fab_process.daemon = True
            self.fab_process.start()
            self.log("FABRICATION: Started task thread")
        else:
            self.log("FABRICATION: No tasks available")

    def stop(self):
        self.close()
        self.log("FABRICATION: Stopped all processes")

    def close(self):
        if self.fab_process is not None:
            self.fab_process.join(timeout=0.1)
            self.fab_process = None

    def reset(self):
        self.stop()
        for task in self.tasks.values():
            task.reset()
        self.clear_log()
        self.log("FABRICATION: Done resetting all tasks")

    def log(self, msg):
        if isinstance(msg, list):
            for m in msg:
                self.log(m)
        else:
            if str(msg) not in self.log_messages:
                self.log_messages.append(str(msg))
                print(str(msg))

    def poll_logs(self):
        """
        Non-blocking polling of the log queue. Call this method periodically
        in the main process to retrieve and print log messages.
        """
        logs = []
        while True:
            try:
                msg = self.results.get_nowait()
                logs.append(msg)
            except Exception:
                break
        return logs

    def clear_log(self):
        self.log_messages= []
    
    def interrupt(self):
        """Interrupt the task loop, terminate running processes, and stop execution."""
        self.interrupt_event.set()
        if self.fab_process and self.fab_process.is_alive():
            self.fab_process.terminate()
            self.fab_process.join()
            self.fab_process = None
        for task in self.tasks.values():
            if task.process and task.process.is_alive():
                task.terminate()
        self.results.put("FABRICATION: INTERRUPTED")
            

if __name__ == '__main__':
    from fabrication_manager.task import Task
    # fab = FabricationManager(server_address=("localhost", 50006))
    fab = FabricationManager()
    # Add tasks: sequential tasks (parallelizable False) and parallel tasks (parallelizable True)
    fab.add_task(Task(0, parallelizable=False))
    fab.add_task(Task(1, parallelizable=True))
    fab.add_task(Task(2, parallelizable=True))
    fab.add_task(Task(3, parallelizable=False))
    
    fab.start()
    
    # Main loop: poll logs and simulate external interruption.
    try:
        start_time = time.time()
        while fab.fab_process.is_alive():
            for log in fab.poll_logs():
                print("LOG:", log)
            print("Main program working...")
            time.sleep(0.5)
            # For demonstration, interrupt after 3 seconds.
            if time.time() - start_time > 3:
                print("Interrupting process...")
                fab.interrupt()
                break
    except KeyboardInterrupt:
        fab.interrupt()
    
    for log in fab.poll_logs():
        print("LOG:", log)
    print("Main program finished.")