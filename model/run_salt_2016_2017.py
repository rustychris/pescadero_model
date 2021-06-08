"""
Runs targeting the 2016/2017 period of the BML field data
"""
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

##

model=pesca_base.PescaButano(run_start=np.datetime64("2016-07-10 00:00"),
                             run_stop=np.datetime64("2016-07-14 00:00"),
                             run_dir="run_salt_20160520-v78",
                             salinity=True,
                             temperature=True,
                             nlayers_3d=28,
                             pch_area=2.0,
                             num_procs=16)

#model.mdu['numerics','CFLmax']=0.8 

# Diagnosing time step slowdown
# model.mdu['time','Timestepanalysis']=1
model.mdu['time','AutoTimestep']=4 # 5=bad. 4 okay but slower, seems no better than 3.

model.mdu['output','MapInterval']=4*3600

# model.mdu['numerics','TurbulenceModel']=1 # 0: dead run.  1: should be 5e-5.
# model.mdu['physics','Vicoww']=5e-3 # 100x greater than before

# Does a saline IC help at all?
model.mdu['physics','InitialSalinity']=32.0

# Try bumping up friction (if this looks promising, will make it just for
# upper channels, use something lower for lagoon, and something high-ish
# for marsh.
model.mdu['physics','UnifFrictCoef']=0.01

# model.mdu['numerics','Limtypsa']=22
# model.mdu['numerics','Limtyptm']=22

# model.mdu['geometry','Keepzlayeringatbed']=0 # spurious velocities and mixing?
#model.mdu['numerics','Vertadvtypsal']=1 
# model.mdu['numerics','TransportMethod']=0
# model.mdu['physics','Dicoww']=0.0

model.write()
model.partition()
model.run_simulation()

