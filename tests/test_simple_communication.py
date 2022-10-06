import time
from fabrication_manager import FabricationManager
from fabrication_manager import TCPFeedbackServer
from ur_fabrication_control.direct_control import URTask, urscript
from ur_fabrication_control.direct_control import URScript

ur_address = ("192.168.56.102", 30002)
server_address = ("192.168.56.103", 50003)

server = TCPFeedbackServer(server_address[0], server_address[1])
ur_script = URScript(ur_address[0], ur_address[1])

# Simple URScript
ur_script.start()
ur_script.socket_open(server_address[0], server_address[1], "FBserver")
ur_script.get_current_pose_cartesian("FBserver", send=True)
ur_script.socket_close("FBserver")
ur_script.end()
ur_script.generate()

server.start()
ur_script.send_script()
time.sleep(1)
server.shutdown
print(server.msgs)

