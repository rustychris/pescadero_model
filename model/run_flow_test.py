import six
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

six.moves.reload_module(hydro_model)
six.moves.reload_module(dflow_model)
six.moves.reload_module(pesca_base)

# Nice flow event
model=pesca_base.PescaButano(run_start=np.datetime64("2017-01-06 00:00"),
                             run_stop=np.datetime64("2017-01-09 00:00"),
                             run_dir="run_flow_test")

model.write()
model.partition()
model.run_simulation()


