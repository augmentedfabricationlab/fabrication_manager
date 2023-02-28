import time
import sys
import threading
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
                self.server.add_message(data)
                msg = "Message from client: {}\n".format(data)
                self.wfile.write(msg.encode())
            except socket.error:
                connected = False 
        print("Client disconnected")
        self.request.close()


class TCPFeedbackServer(ss.TCPServer):
    allow_reuse_address = True
    allow_reuse_port = True

    def __init__(self, ip="192.168.10.11", port=50002,
                 handler=FeedbackHandler):
        if issubclass(TCPFeedbackServer, object):
            super(TCPFeedbackServer, self).__init__((ip,port), handler)
        else:
            ss.TCPServer.__init__(self, (ip, port), handler)
        self.name = "Feedbackserver"
        self.msgs = {}

    def __enter__(cls):
        cls.start()
        print("Enter context: Server started...")
        return cls

    def __exit__(cls, typ, val, tb):
        cls.stop()
        print("Exit context: Server is shut down")

    def clear(self):
        self.msgs = {}

    def stop(self):
        self.shutdown()
        self.server_close()
        self.t.join()

    def start(self):
        self.t = threading.Thread(target=self.serve_forever)
        self.t.start()
        print("Server started in thread...")

    def add_message(self, msg):
        print("Adding message: {}".format(msg))
        if all(i in msg for i in ["[", "]", ","]):
            msg = msg.split('[', 1)[1].split(']')[0]
            msg = msg.split(',')
            msg = [eval(x) for x in msg]
        self.msgs[len(self.msgs)] = msg


if __name__ == '__main__' and sys.version_info[0] == 2:
    import socket

    class socket2(socket.socket):
        def __enter__(cls):
            return cls
        
        def __exit__(cls, typ, val, tb):
            cls.close()
        

    address = ('localhost', 10)
    # let the kernel give us a port
    with TCPFeedbackServer(ip=address[0], port=address[1], handler=FeedbackHandler) as server:
        ip, port = server.server_address
        # find out what port we were given
        # Connect to the server
        with socket2(socket.AF_INET, socket.SOCK_STREAM) as s:
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

    print(server.msgs)

elif __name__ == "__main__" and sys.version_info[0] == 3:
    import socket

    address = ('localhost', 10)
    # let the kernel give us a port
    with TCPFeedbackServer(ip=address[0], port=address[1], handler=FeedbackHandler) as server:
        ip, port = server.server_address
        # find out what port we were given
        # Connect to the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
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

    print(server.msgs)