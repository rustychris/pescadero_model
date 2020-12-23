import pesca_base

class PescaDrainTest(PescaButanoBase):
    run_start=np.datetime64("2015-01-01")
    run_stop =np.datetime64("2015-01-03")
    run_dir="run-draintest"

    def set_bcs(self):
        t_mid=self.run_stop-np.timedelta64(1,'D')
        
        z_da=xr.DataArray([6,-1,-1],
                          dims=('time',),
                          coords=dict(time=[self.run_start,t_mid,self.run_stop]))
        self.add_bcs(hm.StageBC(name='ocean_bc',water_level=z_da))
        
    
