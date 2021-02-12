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
    salinity=True
    temperature=True
    
    def __init__(self,*a,**k):
        super(PescaButanoBase,self).__init__(*a,**k)

        # No horizontal viscosity or diffusion
        self.mdu['physics','Vicouv']=0.0
        self.mdu['physics','Dicouv']=0.0

        # Initial bedlevtype was 3: at nodes, face levels mean of node values
        # Try 4: at nodes, face levels min. of node values
        self.mdu['geometry','BedLevType']=4
        
        self.mdu['output','StatsInterval']=300 # stat output every 5 minutes?
        self.mdu['output','MapInterval']=6*3600 # 6h.
        self.mdu['output','RstInterval']=4*86400 # 4days

        self.mdu['physics','UnifFrictCoef']=0.023 # just standard value.

        if self.salinity:
            self.mdu['physics','Salinity']=1
            self.mdu['physics','InitialSalinity']=0.0
        else:
            self.mdu['physics','Salinity']=0
        if self.temperature:
            self.mdu['physics','Temperature']=1
            self.mdu['physics','InitialTemperature']=18.0 # rough pull from plots
        else:            
            self.mdu['physics','Temperature']=0

        if self.salinity or self.temperature:
            self.mdu['physics','Idensform']=2 # UNESCO
        else:
            self.mdu['physics','Idensform']=0 # no density effects
            
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
        print("Call to add_monitoring")
        self.add_monitor_points(self.match_gazetteer(geom_type='Point',type='monitor'))
        self.add_monitor_sections(self.match_gazetteer(geom_type='LineString',type='transect'))

    def add_structures(self):
        self.add_pch_structure()
        self.add_nmc_structure()
        self.add_nm_ditch_structure()
        self.add_mouth_structure()
        
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

    def add_mouth_structure(self):
        # The mouth may require some testing...
        # For now, will try using the opening width to set width
        # rather than CrestWidth. CrestLevel sets lower edge,
        self.add_Structure(
            type='gate',
            name='mouth',
            # here the gate is never overtopped
            GateHeight=10.0, # top of door to bottom of door
            GateLowerEdgeLevel=0.2, # elevation of bottom of 'gate'
            GateOpeningWidth=5.0, # width of opening. 
            CrestLevel=0.2, # roughly matches bathy.
            # CrestWidth=0.3, # should be the length of the edges
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
        # timing. Comparing time of high tide at a subordinate
        # stations (Ano Nuevo) and short-term harmonic station
        # (Pillar Point) to SF and Monterey further confirms
        # that Pescadero is probably very close to Monterey.
        
        # TODO: need to account for wave climate.
        ocean_bc=hm.NOAAStageBC(name='ocean_bc',station=9413450,
                                     cache_dir=cache_dir)
        self.add_bcs(ocean_bc)
        if self.salinity:
            # ballpark value pulled from BML time series
            ocean_salt=hm.ScalarBC(parent=ocean_bc,scalar='salinity',value=33.0)
            self.add_bcs([ocean_salt])
        if self.temperature:
            # ballpark value pulled from BML time series during open mouth,
            # lower sensor at NCK.
            ocean_temp=hm.ScalarBC(parent=ocean_bc,scalar='temperature',value=15.0)
            self.add_bcs([ocean_temp])

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

        # salinity: will default to 0.0 anyway.
        
        if self.temperature:
            for ck in [bc_butano,bc_pesca]:
                ck_temp=hm.ScalarBC(parent=ck,scalar='temperature',value=18)
                self.add_bcs([ck_temp])
                
        
