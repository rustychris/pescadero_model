"""
Runs targeting the 2016/2017 period of the BML field data
"""
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

## 
model=pesca_base.PescaButano(run_start=np.datetime64("2016-05-20 00:00"),
                             run_stop=np.datetime64("2016-06-20 00:00"),
                             run_dir="run_salt_20160520-v05",
                             qcm_time_offset=np.timedelta64(0,'D'),
                             salinity=True,
                             temperature=True)

model.write()
model.partition()
model.run_simulation()

