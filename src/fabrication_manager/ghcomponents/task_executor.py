import time
import multiprocessing

multiprocessing.set_executable(r"C:\Users\gido\.rhinocode\py39-rh8\python.exe")

if run:
    task = tasks[idx]
    task.reset()
    task.start(results, interrupt_event)
    if wait:
        task.join()

if update:
    if tasks[idx].process is not None and not tasks[idx].process.is_alive():
        tasks[idx].join()
    for i in range(10):
        try:
            msg = results.get_nowait()
            print("LOG:", msg)
        except:
            pass