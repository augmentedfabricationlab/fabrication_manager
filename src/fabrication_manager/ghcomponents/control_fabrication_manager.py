''' 
------------------------------------------------------
/// The code in the Grasshopper "Control Fabrication Manager" component ///
------------------------------------------------------
Component Inputs:
fabrication: FabricationManager
start: Boolean
prev: Boolean
skip: Boolean
stop: Boolean
reset: Boolean

Component Outputs:
None
'''
if start:
    #if robot.is_connected(): #and arduino.is_connected():
    print("starting process")
    fabrication.start()

if prev:
    current_task = fabrication.get_next_task()
    if fabrication.tasks[current_task.key-1]:
        fabrication.tasks[current_task.key-1].reset()

if skip:
    current_task = fabrication.get_next_task()
    current_task.is_completed = True

if stop:
    print("stopping process")
    fabrication.stop()
    
if reset:
    print("resetting process")
    fabrication.reset()