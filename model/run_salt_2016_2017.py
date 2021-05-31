"""
Runs targeting the 2016/2017 period of the BML field data
"""
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

##

model=pesca_base.PescaButano(run_start=np.datetime64("2016-06-01 00:00"),
                             run_stop=np.datetime64("2016-06-30 12:00"),
                             run_dir="run_salt_20160520-v63",
                             salinity=True,
                             temperature=True,
                             nlayers_3d=28,
                             num_procs=16)

#model.mdu['numerics','CFLmax']=0.8 

# Diagnosing time step slowdown
# model.mdu['time','Timestepanalysis']=1
model.mdu['time','AutoTimestep']=4 # 5=bad. 4 okay but slower, seems no better than 3.
model.mdu['numerics','TurbulenceModel']=1 # 0: dead run.  1: should be 5e-5.
# model.mdu['numerics','Turbulenceadvection']=0 # had been 3, but maybe that's causing issues?
model.mdu['physics','Vicoww']=5e-3 # 100x greater than before

model.write()
model.partition()
model.run_simulation()

