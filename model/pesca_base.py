"""
Base subclass of DFlowModel for Pescadero-Butano domain
"""
import os
import xarray as xr
import numpy as np
import pandas as pd

import stompy.model.delft.dflow_model as dfm
import stompy.model.hydro_model as hm
import local_config

here=os.path.dirname(__file__)

class PescaButanoBase(local_config.LocalConfig,dfm.DFlowModel):
    run_start=np.datetime64("2015-01-01")
    run_stop =np.datetime64("2015-01-03")
    run_dir="run"

    terrain='existing'
    
    def __init__(self,*a,**k):
        super(PescaButanoBase,self).__init__(*a,**k)

        self.set_grid_and_features()
        self.set_bcs()
        self.add_monitoring()
        
    def set_grid_and_features(self):
        # For now the only difference is the DEM. If they diverge, might go
        # with separate grid directories instead (maybe with some common features)
        self.set_grid(f"../grids/pesca_butano_v00/pesca_butano_v00_{self.terrain}_bathy.nc")
        self.add_gazetteer("../grids/pesca_butano_v00/line_features.shp")
        self.add_gazetteer("../grids/pesca_butano_v00/point_features.shp")

    def set_bcs(self):
        raise Exception("set_bcs() must be overridden in subclass")

    def add_monitoring(self):
        self.add_monitor_points(self.match_gazetteer(geom_type='Point',type='monitor'))
        self.add_monitor_sections(self.match_gazetteer(geom_type='LineString',type='transect'))

class PescaButano(PescaButanoBase):
    def set_bcs(self):
        self.set_creek_bcs()
        self.set_mouth_bc()

    def set_mouth_bc(self):
        self.add_bcs(hm.StageBC(name='ocean_bc',water_level=1.0))

    def set_creek_bcs(self):
        df=pd.read_csv(os.path.join(here,"../forcing/tu_flows/TU_flows_SI.csv"),
                       parse_dates=['time'])

        def extract_da(desc):
            df_desc=df[ df.flow_desc==desc ]
            ds=xr.Dataset.from_dataframe(df_desc.loc[:,['time','flow_cms']].set_index('time'))
            return ds['flow_cms']

        da_butano=extract_da('Impaired flow Butano TIDAL')
        da_pesca =extract_da('Impaired flow Pe TIDAL')

        bc_butano=hm.FlowBC(name='butano_ck',flow=da_butano)
        bc_pesca =hm.FlowBC(name='pescadero_ck',flow=da_pesca)
        
        self.add_bcs([bc_butano,bc_pesca])
        
