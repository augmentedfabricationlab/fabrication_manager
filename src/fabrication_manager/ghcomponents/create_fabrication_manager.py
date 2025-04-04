''' 
------------------------------------------------------
/// The code in the Grasshopper "Create Fabrication Manager" component ///
------------------------------------------------------
Component Inputs:
create: Boolean
tasks: List[Task]
set_tasks: Boolean

Component Outputs:
fabrication: FabricationManager
'''

from scriptcontext import sticky as st
from fabrication_manager import FabricationManager

if init:
    fabrication = FabricationManager()
    st["fabrication"] = fabrication

if clear:
    st.pop("fabrication")

if "fabrication" not in st:
    fabrication = None
else:
    fabrication = st["fabrication"]

if set_tasks:
    print("setting tasks")
    fabrication.clear_tasks()
    fabrication.set_tasks(tasks)


