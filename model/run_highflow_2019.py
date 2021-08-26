"""
Runs targeting the 2016/2017 period of the BML field data.
Here focused on 2D runs and how various mouth treatments alter
the stage results.
"""
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pesca_base
import os
import shutil
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy import utils
#from stompy.grid import unstructured_grid
import xarray as xr

##
class PescaHighFlow(pesca_base.PescaButano):
    """
    Adjust input data to run recent period not covered by most of
    the datasets used for the 2016/2017 runs
    """
    def set_mouth_bc(self):
        self.log.warning("Have to disable Hsig adjustment FIX")
        self.set_mouth_stage_noaa(hsig_adjustment=False)
    def update_initial_water_level(self):
        self.log.warning("QCM doesn't cover initial condition, fall back to BC")
        super(PescaButanoBase,self).update_initial_water_level()

    def prep_qcm_data(self):
        # Add later data for a static, open mouth
        ds=super(PescaHighFlow,self).prep_qcm_data().copy()
        t_max=ds.time.max()
        extra=ds.isel(time=slice(-2,None)).copy(deep=True)
        pad=np.timedelta64(1,'D')
        extra['time']=('time',),np.r_[self.run_start-pad,self.run_stop+pad]
        extra['z_thalweg']=0.7
        extra['w_inlet']=55
        ds_combine=xr.concat([ds,extra],dim='time')
        return ds_combine
        
    # Use default mouth handling - two frictional structures
    
model=PescaHighFlow(run_start=np.datetime64("2019-02-10 00:00"),
                    run_stop=np.datetime64("2019-02-20 00:00"),
                    run_dir="data_highflow_v019",
                    salinity=False,
                    temperature=False,
                    nlayers_3d=0,
                    pch_area=2.0)

model.mdu['output','MapInterval']=1800

## 
model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

# v019: Flow event -- probably won't work due to missing qcm data

