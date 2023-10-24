# from fabrication_manager.task import Task
import asyncio

# class Task_async(Task):
#     def __init__(self, key=None):
#         super(Task_async, self).__init__(key)    
#         self.initialized = False

#     async def initialize(self):
#         self.initialized = True
#         await asyncio.sleep(1)
#         print("AA: Task {}: Initialized".format(self.key))

#     async def is_initialized(self):
#         while not self.initialized:
#             await asyncio.sleep(0.1)    

async def run_task_async(task):
    print("BB: Task {}: Waiting...".format(task.key))
    await task.is_initialized()
    print("BB: Task {}: Initialization Complete".format(task.key))
    await asyncio.sleep(task.key)
    task.run()
    print("BB: Task {}: Completed".format(task.key))

async def in_sequence(tasks):
    for task in tasks:
        await run_task_async(task)

async def initialize_task(task):
    import random
    await asyncio.sleep(random.randint(0,500)/100)
    task.initialized = True
    task.log("Initialized")

async def is_initialized(task):
    while not task.initialized:
        await asyncio.sleep(0.1)    

async def initialize_tasks(tasks, workers=4):
    sem = asyncio.Semaphore(workers)
    async def sem_task(task):
        async with sem:
            return await initialize_task(task)
    return await asyncio.gather(*(sem_task(t) for t in tasks))

async def initialize_async_run_in_sequence(tasks):
    await asyncio.gather(
        initialize_tasks(tasks),
        in_sequence(tasks)
    )

async def main(tasks):
    # Create a "cancel_me" Task
    print(tasks)
    
    # ftask = asyncio.create_task(in_sequence(tasks))
    ftask = asyncio.create_task(initialize_tasks(tasks))
    # ftask = asyncio.create_task(initialize_async_run_in_sequence(tasks))
    return await ftask

def test_async(tasks=None):
    if tasks is None:
        from fabrication_manager import Task
        tasks = [Task(i) for i in range(10)]
    asyncio.run(main(tasks))
    return [t.log_messages for t in tasks]
    # loop = asyncio.get_event_loop()
    # loop. asyncio.run(main())

if __name__ == "__main__":
    test_async()