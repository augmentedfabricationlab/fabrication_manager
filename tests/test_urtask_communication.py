import time
from fabrication_control import Fabrication
from fabrication_control import TCPFeedbackServer
from ur_fabrication_control.direct_control import URTask, urscript
from ur_fabrication_control.direct_control import URScript

ur_address = ("192.168.56.102", 30002)
server_address = ("192.168.56.104", 50003)

server = TCPFeedbackServer(server_address[0], server_address[1])
ur_script = URScript(ur_address[0], ur_address[1])

# Simple URScript
ur_script.start()
ur_script.socket_open(server_address[0], server_address[1], "FBserver")
ur_script.get_current_pose_cartesian("FBserver", send=True)
ur_script.socket_send_line_string('Done', "FBserver")
ur_script.socket_close("FBserver")
ur_script.end()
ur_script.generate()

urtask = URTask(server, ur_script, "Done", key=0)

server.start()

stop_thread = False
try:
    print("Starting to perform")
    while not urtask.is_completed:
        urtask.perform(stop_thread)
    else:
        print("Task completed")
        if urtask.is_running:
            print("Waiting for task to end")
            while urtask.is_running:
                urtask.perform(stop_thread)
except KeyboardInterrupt:
    print("User interruption")
    stop_thread = True
    urtask.perform(stop_thread)

print(urtask.log_messages)
time.sleep(1)
server.shutdown()
print(server.msgs)

