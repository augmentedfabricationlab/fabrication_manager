from __future__ import absolute_import
import time
import sys
import threading
import socket
if sys.version_info[0] == 2:
    import SocketServer as ss
elif sys.version_info[0] == 3:
    import socketserver as ss
ss.TCPServer.allow_reuse_address = True

__all__ = [
    'FeedbackHandler',
    'TCPFeedbackServer'
]

class FeedbackHandler(ss.StreamRequestHandler):
    def handle(self):
        print("Connected to client at {}".format(self.client_address[0]))
        connected = True
        while connected:
            try:
                data = self.rfile.readline().strip().decode()
                if not data:
                    break
                self.server.rcv_msg.append(data)
                msg = "Message from client: {}\n".format(data)
                self.wfile.write(msg.encode())
            except socket.error:
                connected = False 
        print("Client disconnected")
        self.request.close()               


class TCPServer(ss.TCPServer):
    allow_reuse_address = True


class TCPFeedbackServer(object):
    def __init__(self, ip="192.168.10.11", port=50002,
                 name="FeedbackServer", handler=FeedbackHandler):
        self.ip = ip
        self.port = port
        self.handler = handler
        self.name = name
        self.server = TCPServer((self.ip, self.port), self.handler)
        self.server.rcv_msg = []
        self.msgs = {}
        self._stop_flag = True
        
    def __enter__(cls):
        cls.start()
        print("Enter context: Server started...")
        return cls

    def __exit__(cls, typ, val, tb):
        cls.shutdown()
        print("Exit context: Server is shut down")
        
    def clear(self):
        self.server.rcv_msg = []
        self.msgs = {}

    def _create_thread(self):
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def _create_process_thread(self):
        self.process_thread = threading.Thread(target=self.process_messages,
                                               args=(lambda: self._stop_flag,))
        self.process_thread.daemon = True

    def shutdown(self):
        self._stop_flag = True
        if hasattr(self, "server_thread"):
            self.server.shutdown()
            self.server_thread.join()
            del self.server_thread
        if hasattr(self, "process_thread"):
            self.process_thread.join()
            del self.process_thread

    def start(self, process=True):
        self.shutdown()
        self._stop_flag = False
        self._create_thread()
        self.server_thread.start()
        print("Server started in thread...")
        if process:
            self._create_process_thread()
            self.process_thread.start()
            print("Processing messages...")

    def run(self):
        try:
            self.server.serve_forever()
        except:
            pass

    def process_messages(self, _stop_flag, timeout=None):
        tCurrent = time.time()
        while True:
            if _stop_flag():
                break
            if self.server.rcv_msg is []:
                pass
            elif len(self.msgs) != len(self.server.rcv_msg):
                self.add_message(self.server.rcv_msg[len(self.msgs)])
            if timeout is not None:
                if time.time() >= tCurrent + timeout:
                    print("Listening to server timed out")
                    break

    def add_message(self, msg):
        print("Adding message: {}".format(msg))
        if all(i in msg for i in ["[", "]", ","]):
            msg = msg.split('[', 1)[1].split(']')[0]
            msg = msg.split(',')
            msg = [eval(x) for x in msg]
        self.msgs[len(self.msgs)] = msg


if __name__ == '__main__':
    import socket
    address = ('localhost', 50003)
    # address = ('192.168.56.103', 50003)
    # let the kernel give us a port
    server = TCPFeedbackServer(ip=address[0], port=address[1],
                               handler=FeedbackHandler)
    ip, port = server.server.server_address
    # find out what port we were given

    server.start(process=True)
    # Connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))

    # Send the data
    message = 'Hello, world\n'
    print('Sending : "%s"' % message)
    len_sent = s.send(message.encode())

    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response)

    message = '[0.11,0.11,0.11,0.11,0.11,0.11]\n'
    print('Sending : "%s"' % message)
    len_sent = s.send(message.encode())

    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response)

    message = 'Done\n'
    print('Sending : "%s"' % message)
    len_sent = s.send(message.encode())

    # Receive a response
    response = s.recv(1024).decode('utf8')
    print('Received: "%s"' % response)

    # try:
    #     while True:
    #         pass
    # except KeyboardInterrupt:
    #     pass
    # Clean up
    s.close()
    print("socket closed")
    server.shutdown()
    if "Done" in server.msgs.values():
        print("Found it!")
    print(server.msgs)
    print("Server is shut down")