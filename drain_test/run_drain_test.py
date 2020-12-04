import six
import drain_v00
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid


six.moves.reload_module(hydro_model)
six.moves.reload_module(dflow_model)
six.moves.reload_module(drain_v00)

model=drain_v00.PescaButano()

model.write()
model.partition()
model.run_simulation()


