import sys
from threading import Thread
from .fabrication import Fabrication
from ..communication import TCPFeedbackServer
if sys.version_info[0] == 3:
    from queue import Queue
else:
    from Queue import Queue

__all__ = [
    "FabricationFeedbackServer",
    "Fabrication_with_server"
]


class FabricationFeedbackServer(TCPFeedbackServer):
    def listen_for_msg(self, stop, q):
        req_msg = None
        while True:
            if stop():
                break
            if req_msg is None and not q.empty():
                req_msg = q.get()
            elif req_msg in self.msgs.values():
                q.task_done()
                req_msg = None
            if self.server.rcv_msg is []:
                pass
            elif len(self.msgs) != len(self.server.rcv_msg):
                self.add_message(self.server.rcv_msg[len(self.msgs)])


class Fabrication_with_server(Fabrication):
    def __init__(self):
        super().__init__()
        self.server = None

    def set_feedback_server(self, ip, port):
        self.server = FabricationFeedbackServer(ip, port)

    def close(self):
        self._join_threads()
        self.server.clear()
        self.server.shutdown()

    def start(self):
        self.server.start()
        super().start()
