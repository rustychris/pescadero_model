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
cache_dir=os.path.join(here,'cache')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)

class PescaButanoBase(local_config.LocalConfig,dfm.DFlowModel):
    """
    Base model domain, including flow structures in default 
    states.  Does not include boundary forcing.
    """
    run_start=np.datetime64("2015-01-01")
    run_stop =np.datetime64("2015-01-03")
    run_dir="run"

    terrain='existing'
    
    def __init__(self,*a,**k):
        super(PescaButanoBase,self).__init__(*a,**k)

        self.set_grid_and_features()
        self.set_bcs()
        self.add_monitoring()
        self.add_structures()
        
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

    def add_structures(self):
        self.add_pch_structure()
        self.add_nmc_structure()
        self.add_nm_ditch_structure()
        # self.add_mouth_structure() # coming soon...
    def add_pch_structure(self):
        self.add_Structure(
            type='gate',
            name='pch_gate',
            GateHeight=1.5, # top of door to bottom of door
            GateLowerEdgeLevel=1.0, # elevation of top of culvert
            GateOpeningWidth=0.0, # gate does not open
            CrestLevel=0.6, # matches bathy.
            CrestWidth=0.5, # total guess
        )
        
    def add_nmc_structure(self):
        self.add_Structure(
            type='gate',
            name='nmc_gate',
            GateHeight=1.0, # top of door to bottom of door
            GateLowerEdgeLevel=1.4, # elevation of top of culvert
            GateOpeningWidth=0.0, # gate does not open
            CrestLevel=1.2, # roughly matches bathy.
            CrestWidth=0.3, # total guess
        )
        
    def add_nm_ditch_structure(self):
        self.add_Structure(
            type='gate',
            name='nm_ditch_gate',
            GateHeight=1.0, # top of door to bottom of door
            GateLowerEdgeLevel=1.4, # elevation of top of culvert
            GateOpeningWidth=0.0, # gate does not open
            CrestLevel=1.2, # roughly matches bathy.
            CrestWidth=0.3, # total guess
        )
        
class PescaButano(PescaButanoBase):
    def set_bcs(self):
        self.set_creek_bcs()
        self.set_mouth_bc()

    def set_mouth_bc(self):
        # self.add_bcs(hm.StageBC(name='ocean_bc',water_level=1.0))
        
        # Tides - this is NOAA gauge at Monterey
        #   Probably a bit early -- Pescadero sits between
        # Monterey and SF gauges, and there is a 3200s lag between
        # those two stations (and slight amplification at SF).
        # Both have NAVD88. ESA waterlevels suggest that (a)
        # observations often have a 1 hr error (late), and (b)
        # Pescadero timing probably pretty close to Monterey
        # timing.
        
        # TODO: need to account for wave climate.
        self.add_bcs( hm.NOAAStageBC(name='ocean_bc',station=9413450,
                                     cache_dir=cache_dir) )

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
        
