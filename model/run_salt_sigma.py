"""
Runs targeting the 2016/2017 period of the BML field data
"""
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

##

class PescaSigma(pesca_base.PescaButano):
    def config_layers(self):
        """
        Handle layer-related config, separated into its own method to
        make it easier to specialize in subclasses.
        Only called for 3D runs.
        """
        self.mdu['geometry','Kmx']=self.nlayers_3d # number of layers
        self.mdu['geometry','LayerType']=1 # sigma
        
        # originally 4. 6 is good for avoid scalar issues, but not for stability
        # 5 is good, and also allows the bed adjustment above to be simple
        self.mdu['geometry','BedlevType']= 5

model=PescaSigma(run_start=np.datetime64("2016-07-10 00:00"),
                 run_stop=np.datetime64("2016-07-14 00:00"),
                 run_dir="run_salt_20160520-v72",
                 salinity=True,
                 temperature=True,
                 nlayers_3d=10,
                 pch_area=2.0,
                 num_procs=16)

#model.mdu['numerics','CFLmax']=0.8 

# Diagnosing time step slowdown
# model.mdu['time','Timestepanalysis']=1
model.mdu['time','AutoTimestep']=4 # 5=bad. 4 okay but slower, seems no better than 3.

# model.mdu['numerics','TurbulenceModel']=1 # 0: dead run.  1: should be 5e-5.
# model.mdu['physics','Vicoww']=5e-3 # 100x greater than before

# Does a saline IC help at all?
model.mdu['physics','InitialSalinity']=32.0

# Try bumping up friction (if this looks promising, will make it just for
# upper channels, use something lower for lagoon, and something high-ish
# for marsh.
model.mdu['physics','UnifFrictCoef']=0.055

# model.mdu['numerics','Vertadvtypsal']=0
# model.mdu['numerics','TransportMethod']=0

model.write()
model.partition()
model.run_simulation()

