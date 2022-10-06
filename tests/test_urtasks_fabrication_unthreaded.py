import time
from fabrication_control import Fabrication
from fabrication_control import TCPFeedbackServer
import fabrication_control
from ur_fabrication_control.direct_control import URTask, urscript
from ur_fabrication_control.direct_control import URScript

ur_address = ("192.168.56.102", 30002)
server_address = ("192.168.56.104", 50005)

server = TCPFeedbackServer(server_address[0], server_address[1])

def get_urscript(req_msg):
    # Simple URScript
    ur_script = URScript(ur_address[0], ur_address[1])
    ur_script.start()
    ur_script.socket_open(server_address[0], server_address[1], "FBserver")
    ur_script.get_current_pose_cartesian("FBserver", send=True)
    ur_script.socket_send_line_string(req_msg, "FBserver")
    ur_script.socket_close("FBserver")
    ur_script.textmessage(req_msg, True)
    ur_script.end()
    ur_script.generate()
    return ur_script

tasks = []
for i in range(5):
    req_msg = "Task {} done".format(i)
    ur_script = get_urscript(req_msg)
    urtask = URTask(server, ur_script, req_msg, key=i)
    tasks.append(urtask)

stop_thread = False

fabrication = Fabrication(server)
fabrication.set_tasks(tasks)
fabrication._stop_thread = stop_thread
fabrication.server.start()
try:
    # fabrication.run(lambda: stop_thread)
    while fabrication.tasks_available():
        if (fabrication.get_next_task() is not None
            and (fabrication.current_task is None
                or (fabrication.current_task.is_completed
                    and not fabrication.current_task.is_running)
                )
            ):
            print("Getting next task...")
            fabrication.current_task = fabrication.get_next_task()
        elif (not fabrication.current_task.is_completed
              or fabrication.current_task.is_running):
            fabrication.current_task.perform(lambda: stop_thread)
            fabrication.log(fabrication.current_task.log_messages)

except KeyboardInterrupt:
    print("User interruption")
    stop_thread = True
    fabrication._stop_thread = stop_thread
    fabrication.current_task.perform(stop_thread)
    fabrication.log(fabrication.current_task.log_messages)

print(fabrication.log_messages)
time.sleep(1)
fabrication.server.shutdown()
print(fabrication.server.msgs)

