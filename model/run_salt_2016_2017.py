"""
Runs targeting the 2016/2017 period of the BML field data
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
class PescaDeeper(pesca_base.PescaButano):
    def update_initial_water_level(self):
        # stand-in while Sophie updates
        super(pesca_base.PescaButanoBase,self).update_initial_water_level()

    def add_mouth_structure(self):
        # Baseline:
        # super(PescaDeeper,self).add_mouth_structure()

        # synthetic DEM instead of structures
        # self.add_mouth_as_bathy()
        self.add_mouth_as_structures()

model=PescaDeeper(run_start=np.datetime64("2016-06-10 00:00"),
                  run_stop=np.datetime64("2016-06-20 00:00"),
                  run_dir="run_salt_20160520-v117",
                  salinity=True,
                  temperature=False,
                  nlayers_3d=100,
                  pch_area=2.0,
                  z_max=2.5,
                  z_min=-0.5,
                  num_procs=16)

model.mdu['output','MapInterval']=12*3600

#model.mdu['numerics','Vertadvtypsal']=4
#model.mdu['numerics','Maxitverticalforestersal']=20
model.mdu['numerics','CFLmax']=0.4

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

