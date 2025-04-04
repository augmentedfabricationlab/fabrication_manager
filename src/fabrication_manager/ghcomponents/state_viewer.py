from scriptcontext import sticky as st

fabrication = st["fabrication"]

if fabrication.fab_process is not None:
    if fabrication.fab_process.is_alive():
        state = "PROCESS RUNNING"
    else:
        state = "PROCESS STOPPED"
else:
    state = "PROCESS UNAVAILABLE"

print(fabrication.get_next_task())
num_tasks = len(fabrication.tasks)
if fabrication.get_next_task() is not None:
    num_current_task = fabrication.get_next_task().key
    num_tasks_left = num_tasks-num_current_task
else:
    num_current_task = "NONE"
    num_tasks_left = "NONE"

for log in fabrication.poll_logs():
    print("LOG: ", log)

log_messages = fabrication.log_messages
