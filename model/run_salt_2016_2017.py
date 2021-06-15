"""
Runs targeting the 2016/2017 period of the BML field data
"""
import pesca_base
import os
import shutil
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

##
class PescaDeeper(pesca_base.PescaButano):
    # has been 3.25.  No better results, but 30% faster or so.
    # z_max=2.0
    def set_grid_and_features(self):
        grid_dir="../grids/pesca_butano_v03"
        self.set_grid(os.path.join(grid_dir, f"pesca_butano_{self.terrain}_bathy.nc"))
        self.add_gazetteer(os.path.join(grid_dir,"line_features.shp"))
        self.add_gazetteer(os.path.join(grid_dir,"point_features.shp"))
        self.add_gazetteer(os.path.join(grid_dir,"polygon_features.shp"))
        

model=PescaDeeper(run_start=np.datetime64("2016-06-10 00:00"),
                  run_stop=np.datetime64("2016-08-14 00:00"),
                  run_dir="run_salt_20160520-v95",
                  salinity=True,
                  temperature=True,
                  nlayers_3d=28,
                  pch_area=2.0,
                  num_procs=32)

model.mdu['time','AutoTimestep']=4 # 5=bad. 4 okay but slower, seems no better than 3.
model.mdu['output','MapInterval']=24*3600

model.mdu['numerics','TurbulenceModel']=3 # 0: breaks, 1: constant,  3: k-eps
model.mdu['physics','Dicoww']=1e-7
model.mdu['numerics','Vertadvtypsal']=6
# model.mdu['numerics','Maxitverticalforestersal']=20
model.mdu['numerics','CFLmax']=0.4

# Set friction from polygon features.
if 1:
    model.mdu['physics','UnifFrictCoef']=0.055
    da=model.friction_dataarray()
    # This will default to the same friction type as UnifFrictType
    bc=hydro_model.RoughnessBC(data_array=da)
    model.add_bcs([bc])

# model.mdu['geometry','Keepzlayeringatbed']=0 # spurious velocities and mixing?

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
model.partition()
model.run_simulation()

