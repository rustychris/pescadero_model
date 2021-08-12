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
    def prep_qcm_data(self):
        # Drop the depth of the thalweg 0.15m

        # Make a copy, since this is cached on self.
        ds=super(PescaDeeper,self).prep_qcm_data().copy()
        ds['z_thalweg'] = ds['z_thalweg'] - 0.15
        return ds

    def update_initial_water_level(self):
        # stand-in while Sophie updates
        super(pesca_base.PescaButanoBase,self).update_initial_water_level()

model=PescaDeeper(run_start=np.datetime64("2016-06-10 00:00"),
                  run_stop=np.datetime64("2016-06-20 00:00"),
                  run_dir="run_salt_20160520-v113",
                  salinity=True,
                  temperature=False,
                  nlayers_3d=100,
                  pch_area=2.0,
                  z_max=2.5,
                  z_min=-0.5,
                  num_procs=16)

# model.mdu['time','AutoTimestep']=2 # 5=bad. 4 okay but slower, seems no better than 2.
model.mdu['output','MapInterval']=12*3600

model.mdu['numerics','TurbulenceModel']=3 # 0: breaks, 1: constant,  3: k-eps
model.mdu['physics','Dicoww']=1e-8
model.mdu['physics','Vicoww']=1e-7

#model.mdu['numerics','Vertadvtypsal']=4
#model.mdu['numerics','Maxitverticalforestersal']=20
model.mdu['numerics','CFLmax']=0.4

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

