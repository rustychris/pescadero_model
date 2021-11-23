"""
Test evaporation
"""
import pesca_base
import os
import shutil
import numpy as np
from stompy import utils
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid
import shapely
if shapely.__version__ < "1.7.":
    print("WARNING: shapely before 1.7 lacks substring(), which is used in the synthetic bathymetry")
from shapely import ops, geometry

##
class PescaEvap(pesca_base.PescaButano):
    # Simplified run -- no tides, no flows,
    # just closed conditions, watch salinity and elevation evolve.
    def set_creek_bcs(self):
        pass

model=PescaEvap(run_start=np.datetime64("2016-10-01 00:00"),
                run_stop=np.datetime64("2016-10-14 00:00"),
                run_dir="data_evap_v002",
                salinity=True,
                temperature=False,
                nlayers_3d=100,
                pch_area=2.0,
                z_max=2.5,
                z_min=-0.5,
                num_procs=16)

model.mdu['output','MapInterval']=12*3600
# Intermediate so we can see any ocean water coming in, too.
model.mdu['physics','InitialSalinity']=25.0

model.mdu['numerics','TurbulenceModel']=3 # 0: breaks, 1: constant,  3: k-eps
model.mdu['physics','Dicoww']=1e-8
model.mdu['physics','Vicoww']=1e-7
model.mdu['numerics','CFLmax']=0.4

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

