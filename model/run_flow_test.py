import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

class PescaOpenMouth(pesca_base.PescaButano):
    def add_mouth_structure(self):
        pass

# Nice flow event
model=PescaOpenMouth(run_start=np.datetime64("2017-01-06 00:00"),
                     run_stop=np.datetime64("2017-01-09 00:00"),
                     run_dir="run_flow_test-v02")

model.write()
model.partition()
model.run_simulation()


