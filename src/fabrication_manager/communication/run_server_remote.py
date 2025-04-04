import os, sys
# Insert the absolute path to the src directory at the start of sys.path.
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
print(src_path)
sys.path.insert(0, src_path)

import argparse
import asyncio
from fabrication_manager.communication.async_server import interactive_main

def parse_args():
    parser = argparse.ArgumentParser(description="Async TCP Server")
    parser.add_argument("--ip", type=str, default="127.0.0.1", help="IP address to bind to")
    parser.add_argument("--port", type=int, default=8888, help="Port number")
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_args()
    print(args)
    asyncio.run(interactive_main(args.ip, args.port))