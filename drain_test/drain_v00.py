"""
Basic testing:
 1. Make sure DFM will load the grid
 2. Initialize domain with high water, and slowly 
    drain through mouth.
"""
import xarray as xr
import numpy as np

import stompy.model.delft.dflow_model as dfm
import stompy.model.hydro_model as hm
import local_config

class PescaButano(local_config.LocalConfig,dfm.DFlowModel):
    num_procs=1
    run_start=np.datetime64("2015-01-01")
    run_stop =np.datetime64("2015-01-03")
    run_dir="run"
    
    def __init__(self,*a,**k):
        super(PescaButano,self).__init__(*a,**k)

        self.set_grid_and_features()
        self.set_bcs()
        
    def set_grid_and_features(self):
        self.set_grid("../grids/pesca_butano_v00/pesca_butano_v00_w_bathy.nc")
        self.add_gazetteer("../grids/pesca_butano_v00/line_features.shp")
        
    def set_bcs(self):
        z_da=xr.DataArray([6,-1],
                          dims=('time',),
                          coords=dict(time=[self.run_start,self.run_stop]))
        self.add_bcs(hm.StageBC(name='ocean_bc',water_level=z_da))
        
