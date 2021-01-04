import numpy as np
import xarray as xr
import stompy.model.hydro_model as hm
import pesca_base

class PescaFillDrain(pesca_base.PescaButanoBase):
    """
    Cycle the ocean BC from -1m NAVD88 to +6
    and back.
    No river flows are included.
    """
    run_start=np.datetime64("2015-07-01")
    run_stop =np.datetime64("2015-07-05")
    run_dir="run-drainfill"

    def set_bcs(self):
        t1=self.run_start+np.timedelta64(1,'D')
        t2=self.run_start+np.timedelta64(2,'D')
        
        z_da=xr.DataArray([-1,6,-1,-1],
                          dims=('time',),
                          coords=dict(time=[self.run_start,
                                            t1,t2,
                                            self.run_stop]))
        self.add_bcs(hm.StageBC(name='ocean_bc',water_level=z_da))
        
    
