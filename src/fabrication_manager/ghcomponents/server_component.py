
''' 
------------------------------------------------------
/// The code in the Grasshopper "Server" component ///
------------------------------------------------------
Component Inputs:
start_server: Boolean
ip_address: String
port_number: Integer

Component Outputs:
None
'''
import os, pathlib
import subprocess
import fabrication_manager

python = pathlib.Path(os.__file__).parents[1] /'python.exe'
server = fabrication_manager.communication.run_server_remote.__file__

assert server

def start_script(ip, port):
    args = [python, server, "--ip", ip, "--port", str(port)]
    # args = [python, server]
    result = subprocess.Popen(args)
    print("Server process started with PID:", result.pid)
    # result.wait()

if start_server:
    start_script(ip_address, port_number)