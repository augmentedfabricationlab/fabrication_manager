from multiprocessing import Queue, Event

if create:
    results = Queue()
    interrupt_event = Event()
