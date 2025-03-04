import os
import subprocess
import shlex

pc = os.path.dirname(__file__)
print(pc)
python = r"C:\Users\gido\.rhinocode\py39-rh8\python.exe"
server = str(os.path.join(pc, "async_server.py"))
assert server
print(server)

def start_script():
    result = subprocess.Popen([python, server])
    print(result)

def start_in_terminal():
    result = subprocess.run([python, server])

if __name__ == "__main__":
    print(__file__)
    # start_script()
    start_in_terminal()