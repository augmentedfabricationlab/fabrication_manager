import sys
import os

# Insert the absolute path to the src directory at the start of sys.path.
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../src'))
sys.path.insert(0, src_path)

import unittest
import time
import logging
from fabrication_manager.fabrication import FabricationManager
from fabrication_manager.task import Task

class TestFabricationManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Configure the logger for our tests.
        logging.basicConfig(level=logging.DEBUG)
        cls.logger = logging.getLogger("TestFabricationManager")
        cls.logger.info("Starting FabricationManager tests.")

    def setUp(self):
        self.logger.debug("Setting up FabricationManager instance for test.")
        # Create a manager instance with no server address.
        self.fm = FabricationManager(server_address=(None, None))

    def tearDown(self):
        self.logger.debug("Tearing down FabricationManager instance for test.")
        # If any processes are still running, interrupt them.
        if self.fm.fab_process and self.fm.fab_process.is_alive():
            self.fm.interrupt()
        time.sleep(0.2)

    def wait_for_completion(self, timeout=10):
        """Helper to wait until the manager's process is finished (or timeout)."""
        self.logger.debug("Waiting for tasks to complete...")
        start = time.time()
        while self.fm.fab_process and self.fm.fab_process.is_alive():
            if time.time() - start > timeout:
                self.logger.warning("Timeout reached. Interrupting FabricationManager.")
                self.fm.interrupt()
                break
            time.sleep(0.1)
        self.logger.debug("Task processing finished or interrupted.")

    def test_sequential_tasks(self):
        self.logger.info("Testing sequential tasks execution.")
        # Create two sequential (non-parallelizable) tasks.
        task1 = Task(0, parallelizable=False)
        task2 = Task(1, parallelizable=False)
        self.fm.add_task(task1)
        self.fm.add_task(task2)
        self.fm.start()
        self.wait_for_completion()

        logs = self.fm.poll_logs()
        self.logger.debug("Logs collected: %s", logs)
        self.assertTrue(any("Starting sequential task 0" in log for log in logs))
        self.assertTrue(any("Finished sequential task 0" in log for log in logs))
        self.assertTrue(any("Starting sequential task 1" in log for log in logs))
        self.assertTrue(any("Finished sequential task 1" in log for log in logs))
        self.logger.info("Sequential tasks test passed. \n ---------------------------------")

    def test_parallel_tasks(self):
        self.logger.info("Testing parallel tasks execution.")
        # Create two parallelizable tasks.
        task1 = Task(0, parallelizable=True)
        task2 = Task(1, parallelizable=True)
        self.fm.add_task(task1)
        self.fm.add_task(task2)
        self.fm.start()
        self.wait_for_completion()

        logs = self.fm.poll_logs()
        self.logger.debug("Logs collected: %s", logs)
        self.assertTrue(any("Starting parallel task 0" in log for log in logs))
        self.assertTrue(any("Starting parallel task 1" in log for log in logs))
        self.assertTrue(any("Finished parallel task 0" in log for log in logs))
        self.assertTrue(any("Finished parallel task 1" in log for log in logs))
        self.logger.info("Parallel tasks test passed. \n ---------------------------------")

    def test_mixed_tasks(self):
        self.logger.info("Testing mixed (sequential and parallel) tasks execution.")
        # Mixed tasks: sequential, parallel, then sequential.
        task1 = Task(0, parallelizable=False)
        task2 = Task(1, parallelizable=True)
        task3 = Task(2, parallelizable=False)
        self.fm.add_task(task1)
        self.fm.add_task(task2)
        self.fm.add_task(task3)
        self.fm.start()
        self.wait_for_completion()

        logs = self.fm.poll_logs()
        self.logger.debug("Logs collected: %s", logs)
        self.assertTrue(any("Starting sequential task 0" in log for log in logs))
        self.assertTrue(any("Starting parallel task 1" in log for log in logs))
        self.assertTrue(any("Starting sequential task 2" in log for log in logs))
        # Ensure the sequential task 2 starts only after the parallel task finishes.
        seq2_index = next(i for i, log in enumerate(logs) if "Starting sequential task 2" in log)
        par_finish = any("Finished parallel task 1" in log for log in logs[:seq2_index])
        self.assertTrue(par_finish)
        self.logger.info("Mixed tasks test passed. \n ---------------------------------")

    def test_interrupt(self):
        self.logger.info("Testing interruption of tasks.")
        # Create a couple of parallelizable tasks that run longer.
        task1 = Task(0, parallelizable=True)
        task2 = Task(1, parallelizable=True)
        self.fm.add_task(task1)
        self.fm.add_task(task2)
        self.fm.start()
        # Let tasks run for a moment.
        time.sleep(1)
        self.fm.interrupt()
        logs = self.fm.poll_logs()
        self.logger.debug("Logs collected after interrupt: %s", logs)
        self.assertTrue(any("FABRICATION: INTERRUPTED" in log for log in logs))
        self.logger.info("Interruption test passed. \n ---------------------------------")

if __name__ == '__main__':
    unittest.main()
