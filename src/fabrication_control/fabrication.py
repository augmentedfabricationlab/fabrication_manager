from threading import Thread, Condition
import time


class Fabrication():
    """The summary line for a class docstring should fit on one line.

    If the class has public attributes, they may be documented here
    in an ``Attributes`` section and follow the same formatting as a
    function's ``Args`` section. Alternatively, attributes may be documented
    inline with the attribute's declaration (see __init__ method below).

    Properties created with the ``@property`` decorator should be documented
    in the property's getter method.

    Attributes:
        attr1 (str): Description of `attr1`.
        attr2 (:obj:`int`, optional): Description of `attr2`.
        attr3 (:obj:`list` of :obj:`str`): Description of `attr3`.

    """
    
    def __init__(self):
        """Example of docstring on the __init__ method.

        The __init__ method may be documented in either the class level
        docstring, or as a docstring on the __init__ method itself.

        Either form is acceptable, but the two should not be mixed. Choose one
        convention to document the __init__ method and be consistent with it.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1 (str): Description of `param1`.
            param2 (:obj:`int`, optional): Description of `param2`. Multiple
                lines are supported.
            param3 (:obj:`list` of :obj:`str`): Description of `param3`.

        """
        self.iterations = 0
        
        self.log_messages = []
        self.log_messages_length = 10
        
        self.run_fabrication_flag = True

        self.tasks = []
        self.current_task = None
        
        self.reset()
        
        
    def set_tasks(self, tasks):
        """Methods are similar to regular functions.

        Note:
            Do not include the `self` parameter in the ``Args`` section.

        Args:
            param1: Description of `param1`.

        Returns:
            int: The return value.
        """ 
        self.tasks = tasks

    def clear_tasks(self):
        self.tasks = []

    def reset(self):
        self.log("RESETTING...")
        self.run_fabrication_flag = True
        self.t = Thread(target = self.run)
        self.t.daemon = True  # OK for main to exit even if instance is still running
        self.t.paused = True  # start out paused
        self.t.state = Condition()
        
    def resume(self):
        self.log("RESUME FABRICATION...")
        with self.t.state:
            self.t.paused = False
            self.t.state.notify()  # unblock self if waiting

    def pause(self):
        self.log("SET TO PAUSE...")
        #with self.t.state:
        self.t.paused = True  # make self block and wait  
    
    def start(self):
        self.resume() 
        self.t.start()
    
    def stop(self):
        self.log("SET TO STOP...")
        if self.is_alive():        
            if self.is_paused():
                self.resume()
                
            self.run_fabrication_flag = False
            try:
                self.join()
            except:
                pass
    
    def join(self):
        self.t.join()
    
    def is_paused(self):
        return self.t.paused
    
    def is_alive(self):
        return self.t.is_alive()
    
    def run(self):
        while len(self.tasks):
            with self.t.state:
                if self.t.paused:
                    self.log("PAUSING FABRICATION...")
                    self.t.state.wait() # block until notified
                
                if self.run_fabrication_flag == False:
                    break
                
                self.current_task = self.tasks[0]         
                ok = self.perform_task(self.current_task)

                if ok:
                    #self.current_task.set_built_state(True)
                    self.tasks.pop(0)
                    self.log("POP TASK OFF THE LIST...")
                    
                else:
                    #self.log("PAUSING FABRICATION...")
                    self.pause()
                
            self.iterations += 1
            
            if self.run_fabrication_flag == False:
                break

        if not len(self.tasks):      
            self.log("ALL TASKS DONE")
        else:
            self.log("FABRICATION STOPPED...")


    def perform_task(self, task):
        """ This method has to be overwitten ... """
        
        self.log("TASK START: ---->>>>>")
        ok = True
        # do something
        if not ok:
            return False
        
        self.log("----<<<<< TASK FINISHED")
        return True
    
    def log(self, msg):
        self.log_messages.append("FABRICATION: " + str(msg))
        if len(self.log_messages) > self.log_messages_length:
            self.log_messages = self.log_messages[-self.log_messages_length:] 
    
    def get_log_messages(self):       
        return "\n".join(self.log_messages) 




