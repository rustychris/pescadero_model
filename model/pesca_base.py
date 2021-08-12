"""
Base subclass of DFlowModel for Pescadero-Butano domain
"""
import os
import xarray as xr
import numpy as np
import pandas as pd

from scipy.interpolate import interp1d
from scipy.interpolate import splev, splrep

import stompy.model.delft.dflow_model as dfm
import stompy.model.hydro_model as hm
from stompy.io.local import cdip_mop
from stompy import utils, filters
from stompy.spatial import linestring_utils
from shapely import geometry
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
    # if salinity or temperature are included, then use this
    # many layers, otherwise just 1 layer
    z_min=-0.25 # Based on low point in lagoon
    z_max=3.25  # Based on highest water level in lagoon
    nlayers_3d=14 # 0.25m layers for z_min/max above
    deep_bed_layer=True # make the deepest interface at least as deep as the deepest node
    
    def __init__(self,*a,**k):
        super(PescaButanoBase,self).__init__(*a,**k)

        # No horizontal viscosity or diffusion
        self.mdu['physics','Vicouv']=0.0
        self.mdu['physics','Dicouv']=0.0

        # Initial bedlevtype was 3: at nodes, face levels mean of node values
        # Try 4: at nodes, face levels min. of node values
        self.mdu['geometry','BedLevType']=4
        
        self.mdu['output','StatsInterval']=300 # stat output every 5 minutes?
        self.mdu['output','MapInterval']=12*3600 # 12h.
        self.mdu['output','RstInterval']=4*86400 # 4days
        self.mdu['output','HisInterval']=900 # 15 minutes
        self.mdu['output','MapFormat']=4 # ugrid output format 1= older, 4= Ugrid

        self.mdu['numerics','MinTimestepBreak']=0.001
        self.mdu['time','AutoTimestep']=3 # 5=bad. 4 okay but slower, seems no better than 3.
        self.mdu['time','AutoTimestepNoStruct']=1 # had been 0
        
        self.mdu['physics','UnifFrictCoef']=0.023 # just standard value.

        if self.salinity:
            self.mdu['physics','Salinity']=1
            self.mdu['physics','InitialSalinity']=32.0
        else:
            self.mdu['physics','Salinity']=0
        if self.temperature:
            self.mdu['physics','Temperature']=1
            self.mdu['physics','InitialTemperature']=18.0 # rough pull from plots
        else:            
            self.mdu['physics','Temperature']=0

        self.mdu['output','Wrimap_waterlevel_s0']=0 # no need for last step's water level
            
        self.set_grid_and_features()
        self.set_bcs()
        self.add_monitoring()
        self.add_structures()
        self.set_friction()

        if self.salinity or self.temperature:
            self.mdu['physics','Idensform']=2 # UNESCO
            # 10 sigma layers yielded nan at wetting front, and no tidal variability.
            # 2D works fine -- seems to bring in the mouth geometry okay.
            # Must be called after grid is set
            self.config_layers()
        else:
            self.mdu['physics','Idensform']=0 # no density effects
        
    def update_initial_water_level(self):
        # To be updated to pull QCM lagoon water level at self.run_start
        self.mdu['geometry','WaterLevIni']=2.6 # to overwrite the lagoon waterlevel
        print('overwritting the initial water level to prescribed value')
            
    def set_grid_and_features(self):
        # For now the only difference is the DEM. If they diverge, might go
        # with separate grid directories instead (maybe with some common features)
        grid_dir="../grids/pesca_butano_v03"
        self.set_grid(os.path.join(grid_dir, f"pesca_butano_{self.terrain}_deep_bathy.nc"))
        self.add_gazetteer(os.path.join(grid_dir,"line_features.shp"))
        self.add_gazetteer(os.path.join(grid_dir,"point_features.shp"))
        self.add_gazetteer(os.path.join(grid_dir,"polygon_features.shp"))

    def friction_dataarray(self,type='manning'):
        polys=self.match_gazetteer(geom_type='Polygon',type=type)

        xyn=np.zeros( (self.grid.Nnodes(),3), np.float64)
        xyn[:,:2]=self.grid.nodes['x']
        # Default to the uniform friction coefficient
        xyn[:,2]=self.mdu['physics','UnifFrictCoef']

        for poly in polys:
            sel=self.grid.select_nodes_intersecting(poly['geom'])
            xyn[sel,2]=poly['n']
        ds=xr.Dataset()
        ds['x']=('sample',),xyn[:,0]
        ds['y']=('sample',),xyn[:,1]
        ds['n']=('sample',),xyn[:,2]
        ds=ds.set_coords(['x','y'])
        da=ds['n']
        return da

    def set_friction(self):
        """
        Set friction from polygon features.
        """
        self.mdu['physics','UnifFrictCoef']=0.055
        da=self.friction_dataarray()
        # This will default to the same friction type as UnifFrictType
        bc=hm.RoughnessBC(data_array=da)
        self.add_bcs([bc])

    def config_layers(self):
        """
        Handle layer-related config, separated into its own method to
        make it easier to specialize in subclasses.
        Only called for 3D runs.
        """
        self.mdu['geometry','Kmx']=self.nlayers_3d # number of layers
        self.mdu['geometry','LayerType']=2 # all z layers
        self.mdu['geometry','ZlayBot']=self.z_min
        self.mdu['geometry','ZlayTop']=self.z_max
        
        # Adjust node elevations to avoid being just below interfaces
        # This may not be necessary.
        z_node=self.grid.nodes['node_z_bed'] # positive up
        kmx=self.nlayers_3d
        z_interfaces=np.linspace(self.z_min,self.z_max,kmx+1)

        write_stretch=False 
        if self.deep_bed_layer:
            grid_z_min=self.grid.nodes['node_z_bed'].min()
            if z_interfaces[0]>grid_z_min:
                self.log.info("Bottom interface moved from %.3f to %.3f to match deepest node of grid"%
                              (z_interfaces[0], grid_z_min))
                z_interfaces[0]=grid_z_min
                self.mdu['geometry','ZlayBot']=grid_z_min
                write_stretch=True
            
        dz_bed=z_interfaces[ np.searchsorted(z_interfaces,z_node).clip(0,kmx)] - z_node
        thresh=min(0.05,0.2*np.median(np.diff(z_interfaces)))
        # will deepen these nodes.  Could push them up or down depending
        # on which is closer, but generally we end up lacking conveyance to
        # err on the side of deepening
        adjust=np.where((dz_bed>0)&(dz_bed<thresh),
                        thresh-dz_bed, 0)
        self.grid.nodes['node_z_bed']-=adjust

        # originally 4. 6 is good for avoid scalar issues, but not for stability
        # 5 is good, and also allows the bed adjustment above to be simple
        self.mdu['geometry','BedlevType']= 5

        if write_stretch:
            # Based on this post:
            # https://oss.deltares.nl/web/delft3dfm/general1/-/message_boards/message/1865851
            self.mdu['geometry','StretchType']=1
            cumul=100*(z_interfaces-z_interfaces[0])/(z_interfaces[-1] - z_interfaces[0])
            # round to 0 decimals to be completely sure the sum is exact.
            # hopefully 1 decimal is okay. gives more even layers when getting up to 25+ layers.
            cumul=np.round(cumul,1)
            fracs=np.diff(cumul)
            # something like 10 10 10 10 10 10 10 10 10 10
            # Best not to make this too long.  100 layers with %.4f is too long for the
            # default partitioning script to handle, and this gets truncated.
            self.mdu['geometry','stretchCoef']=" ".join(["%.1f"%frac for frac in fracs])
        
    def set_bcs(self):
        raise Exception("set_bcs() must be overridden in subclass")

    def add_monitor_transects(self,features,dx=None):
        """
        Add a sampled transect. dx=None will eventually just pull each
        cell along the line.  otherwise sample at even distance dx.
        """
        # Sample each cell intersecting the given feature
        assert dx is not None,"Not ready for adaptive transect resolution"
        for feat in features:
            print(feat)
            pnts=np.array(feat['geom'])
            pnts=linestring_utils.resample_linearring(pnts,dx,closed_ring=False)
            self.log.info("Resampling leads to %d points for %s"%(len(pnts),feat['name']))
            # punt with length of the name -- not sure if DFM is okay with >20 characters
            pnts_and_names=[ dict(geom=geometry.Point(pnt),name="%s_%04d"%(feat['name'][:13],i))
                             for i,pnt in enumerate(pnts) ]
            self.add_monitor_points(pnts_and_names)

    def add_monitoring(self):
        print("Call to add_monitoring")
        self.add_monitor_points(self.match_gazetteer(geom_type='Point',type='monitor'))
        # Bad choice of naming. features labeled 'transect' are for cross-sections.
        # Features labeled 'section' are for sampled transects
        self.add_monitor_sections(self.match_gazetteer(geom_type='LineString',type='transect'))
        self.add_monitor_transects(self.match_gazetteer(geom_type='LineString',type='section'),
                                   dx=5.0)

    def add_structures(self):
        self.add_pch_structure()
        self.add_nmc_structure()
        self.add_nm_ditch_structure()
        self.add_mouth_structure()

    pch_area=0.4*0.5
    def add_pch_structure(self):
        # originally this was a 0.4m x 0.5 m
        # opening. Try instead for a wide, short
        # opening to decease CFL issues.
        z_crest=0.6 # matches bathy.
        width=12.0
        self.add_Structure(
            type='gate',
            name='pch_gate',
            GateHeight=1.5, # top of door to bottom of door
            GateLowerEdgeLevel=z_crest + self.pch_area/width, # elevation of top of culvert
            GateOpeningWidth=0.0, # gate does not open
            CrestLevel=z_crest, 
            CrestWidth=width, # extra wide for decreased CFL limitation
        )
        # Original settings:
        # GateHeight=1.5, # top of door to bottom of door
        # GateLowerEdgeLevel=1.0, # elevation of top of culvert
        # GateOpeningWidth=0.0, # gate does not open
        # CrestLevel=0.6, # matches bathy.
        # CrestWidth=0.5, # total guess

        
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
        """
        Configure structures (or absence of structures) at the mouth
        """
        # Uses two structures:
        self.add_mouth_in_structure()
        self.add_mouth_out_structure()
        
    def add_mouth_in_structure(self):
        """
        Add flow control structure at mouth, for the inner of two structures.
        """
        self.add_Structure(
            type='gate',
            name='mouth_in',
            # here the gate is never overtopped
            GateHeight=10.0, # top of door to bottom of door
            GateLowerEdgeLevel=0.2, # elevation of bottom of 'gate'
            GateOpeningWidth=5.0, # width of opening. 
            CrestLevel=0.2, # roughly matches bathy.
            # CrestWidth=0.3, # should be the length of the edges
        )
        
    def add_mouth_out_structure(self):
        """
        Add flow control structure at mouth, here just the outer of two 
        structures.
        """
        self.add_Structure(
            type='gate',
            name='mouth_out',
            # here the gate is never overtopped
            GateHeight=10.0, # top of door to bottom of door
            GateLowerEdgeLevel=0.2, # elevation of bottom of 'gate'
            GateOpeningWidth=5.0, # width of opening. 
            CrestLevel=0.2, # roughly matches bathy.
            # CrestWidth=0.3, # should be the length of the edges
        )

class PescaButano(PescaButanoBase):
    """ Add realistic boundary conditions to base Pescadero model
    """
    def set_bcs(self):
        self.set_creek_bcs()
        self.set_mouth_bc()

    def set_mouth_bc(self):
        ocean_bc=self.set_mouth_stage_qcm()
        assert ocean_bc,"mouth waterlevel BC method probably should return a BC"
        
        if self.salinity:
            # ballpark value pulled from BML time series
            ocean_salt=hm.ScalarBC(parent=ocean_bc,scalar='salinity',value=33.0)
            self.add_bcs([ocean_salt])
        if self.temperature:
            # ballpark value pulled from BML time series during open mouth,
            # lower sensor at NCK.
            ocean_temp=hm.ScalarBC(parent=ocean_bc,scalar='temperature',value=15.0)
            self.add_bcs([ocean_temp])

    def set_mouth_stage_qcm(self):
        """
        Use the interpolated QCM waterlevel datas as BC.
        Stock QCM output is a bit coarse (dt=1h) for stage, so 
        smooth it at shorter time step
        """
        da=self.prep_qcm_waterlevel_resampled()
        ocean_bc=hm.StageBC(name='ocean_bc',water_level=da)
        self.add_bcs([ocean_bc])
        return ocean_bc
    
    def prep_qcm_waterlevel_resampled(self):
        """
        Upsample the QCM waterlevel data to 6 minutes, smoothed
        with a cubic spline
        """
        qcm_ds=self.prep_qcm_data()
        
        # Apply the spline, no smoothing, to the entire record and return
        # as DataArray

        t_dnum = utils.to_dnum(qcm_ds.time)
        t_new = np.arange(qcm_ds.time.values[0], qcm_ds.time.values[-1],
                          np.timedelta64(6,'m')) # at 6 minutes intervals. 
        t_new_dnum = utils.to_dnum(t_new)

        spl = splrep(t_dnum, qcm_ds.z_ocean.values)
        qcm_wl_interp = splev(t_new_dnum, spl)
        da=xr.DataArray(qcm_wl_interp,dims=['time'],coords=dict(time=t_new))
        return da
        
    def set_mouth_stage_noaa(self):
        """
        Drive water level at the mouth from the NOAA gauge
        at Monterey and an empirical offset accounting for
        wave setup.
        Returns the BC object after adding it to the model
        """
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

        def Hsig_adjustment(da):
            Hsig=cdip_mop.hindcast_dataset(station='SM141', # Pescadero State Beach
                                           start_date=da.time.values[0],
                                           end_date=da.time.values[-1],
                                           clip='inclusive',
                                           cache_dir=cache_dir,
                                           variables=['waveHs'])
            Hsig_colo=np.interp(utils.to_dnum(da.time.values),
                                utils.to_dnum(Hsig.time.values), Hsig['waveHs'].values )
            offset=(0.351*Hsig_colo - 0.230).clip(0)
            # TODO: see if a hanning window lowpass makes the "optimal" window size
            # something shorter, which would seem more physical.
            offset=filters.lowpass_fir(offset,winsize=7*24,window='boxcar')
            return da+offset

        ocean_bc=hm.NOAAStageBC(name='ocean_bc',station=9413450,
                                filters=[hm.Transform(fn_da=Hsig_adjustment),
                                          hm.Lowpass(cutoff_hours=2.5)],
                                cache_dir=cache_dir)
        self.add_bcs(ocean_bc)
        return ocean_bc

    def set_creek_bcs(self):
        df=pd.read_csv(os.path.join(here,"../forcing/tu_flows/TU_flows_SI.csv"),
                       parse_dates=['time'])

        def extract_da(desc):
            df_desc=df[ df.flow_desc==desc ]
            ds=xr.Dataset.from_dataframe(df_desc.loc[:,['time','flow_cms']].set_index('time'))
            return ds['flow_cms']

        da_butano=extract_da('Impaired flow Butano TIDAL')
        da_pesca =extract_da('Impaired flow Pe TIDAL')

        # Dredge shallower than usual to avoid stacking up z layers here.
        # This should mean that other parts of the domain with bathy down to -0.25
        # or so control the z-layer range, but this is still deep enough that initial
        # water level will have this wet.
        # "real" solution is maybe to have a spatially variable initial water level.
        bc_butano=hm.FlowBC(name='butano_ck',flow=da_butano,dredge_depth=0.0)
        bc_pesca =hm.FlowBC(name='pescadero_ck',flow=da_pesca,dredge_depth=0.0)
        
        self.add_bcs([bc_butano,bc_pesca])

        # Seems that salinity defaults to the IC salinity.
        if self.salinity:
            for ck in [bc_butano,bc_pesca]:
                ck_salt=hm.ScalarBC(parent=ck,scalar='salinity',value=0)
                self.add_bcs([ck_salt])
            
        if self.temperature:
            for ck in [bc_butano,bc_pesca]:
                ck_temp=hm.ScalarBC(parent=ck,scalar='temperature',value=18)
                self.add_bcs([ck_temp])

    # time shift for QCM, while we don't have QCM output for
    # the period of the BML data
    qcm_time_offset=np.timedelta64(0,'s')
            
    def add_mouth_in_structure(self):
        """
        Set up the flow control structure for the inner mouth structure
        """
        ds = self.prep_qcm_data()

        crest= ds['z_thalweg']
        width= ds['w_inlet']    

        self.add_Structure(
            type='generalstructure',
            name='mouth_in',
            
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=55,                 	# Width structure left side (m)
            CrestWidth=50,                 	    # Width structure centre (m)
            Downstream1Width=55,                 	# Width structure right side (m)
            Downstream2Width=60,                 	# Width right side of structure (m)
            Upstream2Level=0.25,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.25,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	                    # Bed level at centre of structure (m AD)
            Downstream1Level=0.25,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.25,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=0.2,                  	# Gate lower edge level (m AD)
            pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
            pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
            pos_freeweirflowcoeff=1,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=1,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                   	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=1,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=1,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=4,                   	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            #GateOpeningHorizontalDirection=symmetric,           	# Horizontal direction of the opening doors
            )
        
    def add_mouth_out_structure(self):
        """
        Set up flow control structure for the outer mouth structure
        """
        ds = self.prep_qcm_data()

        crest= ds['z_thalweg']
        width= ds['w_inlet']    
        
        self.add_Structure(
            type='generalstructure',
            name='mouth_out',
            
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=55,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=55,                 	# Width structure right side (m)
            Downstream2Width=60,                 	# Width right side of structure (m)
            Upstream2Level=1,                   	# Bed level left side of structure (m AD)
            Upstream1Level=1,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=1,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=0.2,                  	# Gate lower edge level (m AD)
            pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
            pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
            pos_freeweirflowcoeff=1,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=1,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                   	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=1,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=1,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=1,                   	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            #GateOpeningHorizontalDirection=symmetric,           	# Horizontal direction of the opening doors
            )        

    ds_qcm=None
    def prep_qcm_data(self):
        '''load QCM output and prepare xr dataset'''
        if self.ds_qcm is None:
            qcm_pre2016=pd.read_csv("../../data/ESA_QCM/ESA_draft_PescaderoQCM_output.csv",
                                    skiprows=[0],usecols=range(7),
                                    parse_dates=['Date (PST)'])
            qcm_2016_2017=pd.read_csv("../../data/ESA_QCM/ESA_draft_PescaderoQCM_output_4.28.2021.csv",
                                      skiprows=[0],usecols=range(14),
                                      parse_dates=['Date (PST)'])
            # some extra rows in the csv
            qcm_2016_2017=qcm_2016_2017[ ~qcm_2016_2017['Date (PST)'].isnull() ]
            qcm=pd.concat([qcm_pre2016,qcm_2016_2017], sort=False)

            qcm['time']=qcm['Date (PST)'] + np.timedelta64(8,'h') + self.qcm_time_offset # Shift to UTC.
            # These are both NAVD88, converted ft=>m
            # Prefer the modified data when available:
            ocean_modified=qcm['Modified Ocean Level (feet NAVD88)']
            # Otherwise the observed data.
            ocean_level=qcm['Ocean level (feet NAVD88)']
            qcm['z_ocean']=0.3048 * ocean_modified.combine_first(ocean_level)
            qcm['z_thalweg']=0.3048 * qcm['Modeled Inlet thalweg elevation (feet NAVD88)']

            # width
            qcm['w_inlet']=0.3048* qcm['Modeled Inlet Width (feet)'].fillna(0)
            
            # Other Sources and Sinks: convert form ft3/s to m3/s
            qcm['seepage']= qcm['Modeled seepage'] * 0.02831685 # from ft3/s to m3/s
            qcm['seepage_abs']=qcm['seepage']*-1 # need to be in absolute values
            qcm.loc[qcm['seepage_abs'] < 0,'seepage_abs'] = 0 # removing seepage from ocean to lagoon
                       
            # Values are already [-]. Negative rainfall --> evapotranspiration
            qcm['evapotr']= qcm['Modeled ET'] * 0.02831685 # ft3/s to m3/s
            # evapotr/grid_area*1000 --> m3 to mm
            # *3600 --> s to hour
            # would be better to figure out time-average wet area. This figure is the
            # total grid area.
            grid_area=1940000 # m2
            qcm['evapotr_mmhour']=qcm['evapotr']/grid_area*1000*3600
            # data already [+]            
            qcm['wave_overtop']= qcm['Modeled wave overtopping'] * 0.02831685 # from ft3/s to m3/s

            ds=xr.Dataset.from_dataframe(qcm[ 
                ['time','z_ocean','z_thalweg','w_inlet','seepage_abs','evapotr_mmhour','wave_overtop']]
                .set_index('time'))
            self.qcm_ds=ds
            
        return self.qcm_ds
        
