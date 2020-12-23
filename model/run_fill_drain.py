import six
import pesca_fill_drain
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

# Cycle -1 -- 6 -- -1
model=pesca_fill_drain.PescaFillDrain()

model.write()
model.partition()
model.run_simulation()


