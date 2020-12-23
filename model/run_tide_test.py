import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

# Match up with a bit of the UCB model period
model=pesca_base.PescaButano(run_start=np.datetime64("2012-04-20 00:00"),
                             run_stop=np.datetime64("2012-04-25 00:00"),
                             run_dir="run_tide_test")

model.write()
model.partition()
model.run_simulation()


