"""
Base subclass of DFlowModel for Pescadero-Butano domain
"""
import os,sys
import re
import xarray as xr
import numpy as np
import pandas as pd

from scipy.interpolate import interp1d
from scipy.interpolate import splev, splrep

import stompy.model.delft.dflow_model as dfm
import stompy.model.delft.io as dio
import stompy.model.hydro_model as hm
from stompy.io.local import cdip_mop
from stompy import utils, filters
from stompy.spatial import (linestring_utils, wkb2shp, field)
from shapely import geometry
from stompy.grid import unstructured_grid
import stompy.model.delft.io as dio

import local_config



cache_dir=os.path.join(local_config.model_dir,'cache')
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)


ft_to_m=0.3048

class PescaButanoBaseMixin(local_config.LocalConfig):
    """
    Base model domain, including flow structures in default 
    states.  Does not include boundary forcing.
    """
    run_start=np.datetime64("2015-01-01")
    run_stop =np.datetime64("2015-01-03")
    run_dir="run"

    terrain='existing'
    # scenario=...
    slr=0.0 # [m] applied in prep_qcm_dataset to ocean, lagoon and thalweg elevations
    slr_raise_inlet=True # adjust the nearshore and part of inlet up by SLR, too
    
    salinity=True
    temperature=False
    # if salinity or temperature are included, then use this
    # many layers, otherwise just 1 layer
    z_min=-0.25 # Based on low point in lagoon
    z_max=3.25  # Based on highest water level in lagoon
    nlayers_3d=14 # 0.25m layers for z_min/max above
    deep_bed_layer=True # make the deepest interface at least as deep as the deepest node

    # If true, IC and all BCs are set to 32.0
    debug_salt=False

    # relative to model directory. Grid with no bathymetry
    grid_file="../grids/pesca_butano_v05/quad_tri_v21-edit30.nc"
    
    def configure(self):
        super(PescaButanoBaseMixin,self).configure()
        self.configure_global()
            
        self.set_grid_and_features()
        self.set_bcs()
        self.add_monitoring()
        self.add_structures()
        self.set_friction()

        self.config_layers()

    def configure_global(self):
        """
        global, DFM-specific settings
        """
        # No horizontal viscosity or diffusion
        self.mdu['physics','Vicouv']=0.0
        self.mdu['physics','Dicouv']=0.0

        # Initial bedlevtype was 3: at nodes, face levels mean of node values
        # then 4, at nodes, face levels min. of node values
        # That led to salt mass being introduced erroneously
        # 6 avoided the salt issues, but was not as stable
        # 5 is a good tradeoff, and also allows the bed adjustment above to be simple
        self.mdu['geometry','BedLevType']=5
        
        self.mdu['output','StatsInterval']=300 # stat output every 5 minutes?
        self.mdu['output','MapInterval']=12*3600 # 12h.
        self.mdu['output','RstInterval']=4*86400 # 4days
        self.mdu['output','HisInterval']=900 # 15 minutes
        self.mdu['output','MapFormat']=4 # ugrid output format 1= older, 4= Ugrid

        self.mdu['numerics','MinTimestepBreak']=0.001
        self.mdu['numerics','Epshu']=0.005 # 5mm wet/dry threshold
        self.mdu['numerics','CFLmax']=0.7 # if things go sideways, go back to 0.4

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
            
        if self.salinity or self.temperature:
            self.mdu['physics','Idensform']=2 # UNESCO
            self.mdu['numerics','TurbulenceModel']=3 # 0: breaks, 1: constant,  3: k-eps
            self.mdu['physics','Dicoww']=1e-8
            self.mdu['physics','Vicoww']=1e-6 # used to be 1e-7, but isn't 1e-6 more appropriate?
        else:
            self.mdu['physics','Idensform']=0 # no density effects

        # Trim the map output down to keep files smaller
        self.mdu['output','Wrimap_waterlevel_s0']=0 # no need for last step's water level
        self.mdu['output','Wrimap_velocity_component_u0']=0 #        # Write velocity component for previous time step to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_velocity_component_u1']=0 #        # Write velocity component to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_velocity_vector']=0 #              # Write cell-center velocity vectors to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_upward_velocity_component']=0 #    # Write upward velocity component on cell interfaces (1: yes, 0: no)
        self.mdu['output','Wrimap_density_rho']=0 #                  # Write flow density to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_horizontal_viscosity_viu']=0 #     # Write horizontal viscosity to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_horizontal_diffusivity_diu']=0 #   # Write horizontal diffusivity to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_flow_flux_q1']=0 #                 # Write flow flux to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_spiral_flow']=0 #                  # Write spiral flow to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_chezy']=0 #                        # Write the chezy roughness to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_turbulence']=0 #                   # Write vicww, k and eps to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_wind']=0 #                         # Write wind velocities to map file (1: yes, 0: no)

    def infer_initial_water_level(self):
        """
        Set initial water level to qcm lagoon data, unless
        outside qcm coverage in which case use the BC.
        """
        ds=self.prep_qcm_data()
        if self.run_start>ds.time.min() and self.run_start<ds.time.max():
            tidx=np.searchsorted(ds.time,self.run_start)
            z_init=ds['z_lagoon'].values[tidx]
            return z_init
        else:
            self.log.warning("QCM doesn't cover initial condition, fall back to BC")
            return super(PescaButanoBaseMixin,self).infer_initial_water_level()

    def set_grid_and_features(self):
        # full path to original grid, no bathy.
        self.grid_nobathy_path=os.path.join(local_config.model_dir,self.grid_file)
        # directory holding that grid, and the directory with gazetteer features
        self.grid_dir=os.path.dirname(self.grid_nobathy_path)

        self.grid_with_bathy_path=os.path.join(self.grid_dir,
                                               f"grid_{self.terrain}_deepbathy.nc")
        # Do weirs depend on the grid? no.
        self.fixed_weir_fn=os.path.join(self.grid_dir,f"fixed_weirs-{self.terrain}.pliz")

        # will create grid_with_bathy_path and fixed_weir_fn as needed
        self.add_bathy_to_grid_and_levees()
        
        self.set_grid(self.grid_with_bathy_path)
        
        self.add_gazetteer(os.path.join(self.grid_dir,"line_features.shp"))
        self.add_gazetteer(os.path.join(self.grid_dir,"point_features.shp"))
        self.add_gazetteer(os.path.join(self.grid_dir,"polygon_features.shp"))

        # Check for and install fixed_weirs
        self.fixed_weirs=dio.read_pli(self.fixed_weir_fn)

        if self.slr!=0.0 and self.slr_raise_inlet:
            self.raise_inlet(self.slr)

    def add_bathy_to_grid_and_levees(self):
        bathy_dir=local_config.bathy_dir
        bathy_asbuilt_fn=os.path.join(bathy_dir,'compiled-dem-asbuilt-20210920-1m.tif')
        bathy_existing_fn=os.path.join(bathy_dir,'compiled-dem-existing-20210920-1m.tif')
        
        if self.terrain=='asbuilt':
            dem_fn=bathy_asbuilt_fn
        elif self.terrain=='existing':
            dem_fn=bathy_existing_fn
        else:
            raise Exception(f"Unknown terrain: {self.terrain}")

        assert os.path.exists(dem_fn),f"Failed to find {dem_fn}"

        # Check for stale or missing:
        gen_grid =utils.is_stale(self.grid_with_bathy_path,[dem_fn,self.grid_nobathy_path])
        line_shp=os.path.join(self.grid_dir,'line_features.shp')
        gen_weirs=utils.is_stale(self.fixed_weir_fn, [dem_fn,line_shp])

        self.log.info("New grid with bathy needed? %s"%gen_grid)
        self.log.info("New fixed weirs needed? %s"%gen_weirs)

        if not (gen_grid or gen_weirs):
            return
        
        self.log.info("Loading DEM for %s"%self.terrain)
        dem=field.GdalGrid(dem_fn)

        if gen_weirs:
            lines=wkb2shp.shp2geom(line_shp)
            self.log.info("Generating fixed weirs")
            fixed_weir_fn="fixed_weirs-%s.pliz"%self.terrain
            fixed_weirs=[] # suitable for write_pli
            dx=5.0 # m. discretize lines at this resolution
            for i in range(len(lines)):
                feat=lines[i]
                if feat['type']!='fixed_weir': continue

                self.log.info(f"Processing levee feature {feat['name']}")
                xy=np.array(feat['geom'])
                xy=linestring_utils.upsample_linearring(xy,dx,closed_ring=False)
                z=dem(xy)
                fixed_weirs.append( (feat['name'],
                                     np.c_[xy,z,0*z,0*z]))

            dio.write_pli(self.fixed_weir_fn,fixed_weirs)

        if gen_grid:
            self.log.info("Setting bathymetry on grid")

            g=unstructured_grid.UnstructuredGrid.read_ugrid(self.grid_nobathy_path)
            g.renumber() # just to be sure

            if 0: # Simplest option:
                #   Put bathy on nodes, just direct sampling.
                z_node=dem( g.nodes['x'] )
            if 1: # Bias deep
                # Maybe a good match with bedlevtype=5.
                # BLT=5: edges get shallower node, cells get deepest edge.
                # So extract edge depths (min,max,mean), and nodes get deepest
                # edge.

                alpha=np.linspace(0,1,5)
                edge_data=np.zeros( (g.Nedges(),3), np.float64)

                # Find min/max/mean depth of each edge:
                for j in utils.progress(range(g.Nedges())):
                    pnts=(alpha[:,None] * g.nodes['x'][g.edges['nodes'][j,0]] +
                          (1-alpha[:,None]) * g.nodes['x'][g.edges['nodes'][j,1]])
                    z=dem(pnts)
                    edge_data[j,0]=z.min()
                    edge_data[j,1]=z.max()
                    edge_data[j,2]=z.mean()

                z_node=np.zeros(g.Nnodes())
                for n in utils.progress(range(g.Nnodes())):
                    # This is the most extreme bias: nodes get the deepest
                    # of the deepest points along adjacent edgse
                    z_node[n]=edge_data[g.node_to_edges(n),0].min()

            g.add_node_field('node_z_bed',z_node,on_exists='overwrite')
            g.write_ugrid(self.grid_with_bathy_path,overwrite=True)
        del dem


    def raise_inlet(self,slr):
        scen_shp=wkb2shp.shp2geom(os.path.join(local_config.bathy_dir,"dem-scenarios.shp"))
        poly=scen_shp['geom'][ scen_shp['src_name']=='slr_region'][0]
        inlet_nodes=self.grid.select_nodes_intersecting(poly)
        max_dist=25.0
        dists=self.grid.distance_transform_nodes(inlet_nodes,max_dist)
        weights=(max_dist-dists).clip(0) / max_dist
        assert np.all( np.isfinite(weights) )
        assert weights.max()<=1.0
        assert weights.min()>=0.0
        self.grid.nodes['node_z_bed'][:] += weights*self.slr

    def friction_geometries(self):
        return self.match_gazetteer(geom_type='Polygon',type=type)
        
    def friction_dataarray(self,type='manning'):
        polys=self.friction_geometries()

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
        Now called for 2D and 3D alike
        """
        if (not self.salinity) and (not self.temperature):
            self.mdu['geometry','Kmx']=0 # 2D run
            return
        
        # 10 sigma layers yielded nan at wetting front, and no tidal variability.
        # 2D works fine -- seems to bring in the mouth geometry okay.
        # Must be called after grid is set
                
        self.mdu['geometry','Kmx']=self.nlayers_3d # number of layers
        if self.nlayers_3d>1:
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
        else:
            self.mdu['geometry','LayerType']=1 # sigma

        # These *might* help in 3D...
        # On RH laptop they cause 2D runs to fail during startup.
        self.mdu['time','AutoTimestep']=3 # 5=bad. 4 okay but slower, seems no better than 3.
        self.mdu['time','AutoTimestepNoStruct']=1 # had been 0
        
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
            pnts=np.array(feat['geom'])
            pnts=linestring_utils.resample_linearring(pnts,dx,closed_ring=False)
            self.log.info("Resampling leads to %d points for %s"%(len(pnts),feat['name']))
            # punt with length of the name -- not sure if DFM is okay with >20 characters
            pnts_and_names=[ dict(geom=geometry.Point(pnt),name="%s_%04d"%(feat['name'][:13],i))
                             for i,pnt in enumerate(pnts) ]
            self.add_monitor_points(pnts_and_names)

    def add_monitoring(self):
        self.add_monitor_points(self.match_gazetteer(geom_type='Point',type='monitor'))
        # Bad choice of naming. features labeled 'transect' are for cross-sections.
        # Features labeled 'section' are for sampled transects
        self.add_monitor_sections(self.match_gazetteer(geom_type='LineString',type='transect'))
        self.add_monitor_transects(self.match_gazetteer(geom_type='LineString',type='section'),
                                   dx=20.0)

    def add_structures(self):
        self.add_pch_structure()
        self.add_nmc_structure()
        self.add_nm_ditch_structure()
        self.add_mouth_structure()
        if self.terrain=='asbuilt':
            self.add_butano_weir_structure()

    pch_area = 6*3.1416*0.6**2 # 6 culverts of 2ft radius
    def add_pch_structure(self):
        z_crest=0.5 # The design plans for the culverts put base at -1ft NGVD --> 0.5m NABD88
        height = 1.2 # height of the culverts (48in)
        
        # NOTE: depending on DFM settings, the culvert can create CFL issues. Making
        # CrestWidth longer, and height shorter distributes flow over more edges and
        # can mitigate CFL issues.
        self.add_Structure(
            type='gate',
            name='pch_gate',
            GateHeight=1.5, # top of door to bottom of door
            GateLowerEdgeLevel=z_crest + height, # elevation of top of culvert
            GateOpeningWidth=0.0, # gate does not open
            CrestLevel=z_crest, 
            CrestWidth=self.pch_area/height, # to conserve the same effective cross section
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
        
    def add_butano_weir_structure(self):
        self.add_Structure(
            type='weir',
            name='butano_weir',
            crest_level=2, # based on 2020 BC3 observations
            crest_width=0.6, # total guess from photo
            lat_cont_coeff = 1,
        )         

    def add_mouth_structure(self):
        """
        Configure structures (or absence of structures) at the mouth
        """
        # Uses two structures:
        self.add_mouth_gen_structure(name='mouth_in')
        self.add_mouth_gen_structure(name='mouth_out')
        
    def add_mouth_gen_structure(self,name):
        """
        Add flow control structure at mouth, for the inner of two structures.
        """
        self.add_Structure(
            type='gate',
            name=name,
            # here the gate is never overtopped
            GateHeight=10.0, # top of door to bottom of door
            GateLowerEdgeLevel=0.2, # elevation of bottom of 'gate'
            GateOpeningWidth=5.0, # width of opening. 
            CrestLevel=0.2, # roughly matches bathy.
            # CrestWidth=0.3, # should be the length of the edges
        )

    def centerline_to_node_coordinates(self,center,max_width=50.0):
        """
        Select nodes within max_width/2 of the centerline, 
        and approximate an along/across channel coordinate system.
        Trims the ends to approximate the distance as perpendicular to the
        line. Used in add_mouth_as_bathy()

        center: linestring geometry
        max_width: full width of the swath to consider
        returns node_indexes, d_along, d_across
        node_indexes is in sorted order.
        """
        # Find the collection of nodes that may be relevant.
        region=center.buffer(max_width/2.0)
        node_sel=np.nonzero( self.grid.select_nodes_intersecting(region) )[0]

        # For those nodes calculate longitudinal and lateral coordinates
        node_long=np.r_[ [center.project( geometry.Point(p) )
                          for p in self.grid.nodes['x'][node_sel]] ]

        # And ignore nodes closest to the ends
        good=(node_long>0.0) & (node_long<center.length)
        node_sel=node_sel[good]
        node_long=node_long[good]
        projected=np.array( [np.array(center.interpolate(nlong)) for nlong in node_long] )
        pnts=self.grid.nodes['x'][node_sel]

        node_lat=utils.dist(projected-pnts) # fyi, not really a coordinate, since it's nonnegative
        good=node_lat<=max_width/2.
        node_sel=node_sel[good]
        node_long=node_long[good]
        node_lat=node_lat[good]
        pnts=self.grid.nodes['x'][node_sel]

        # This makes it easier for downstream code to use searchsorted
        assert np.all(np.diff(node_sel)>0)
        # Now I have a local coordinate system (ish)
        return node_sel,node_long,node_lat
            
    def add_mouth_as_bathy(self,plot=False):
        """
        Update bed elevation in the grid to reflect the QCM geometry
        at a specific time (run_start). Uses the 'mouth_centerline' feature
        in the shapefile inputs to define the centerline and which nodes will
        be updated. Bed is static, though.
        """
        # Choose geometry from the start of the period:
        ds=self.prep_qcm_data()
        sel=np.nonzero( ds.time.values>=self.run_start )[0][0]
        qcm_snap=ds.isel(time=sel)
        qcm_width=qcm_snap.w_inlet.item()
        qcm_z_thalweg=qcm_snap.z_thalweg.item()

        # Use thalweg_pesc to guide the center of the synthetic channel
        center=self.match_gazetteer(name='mouth_centerline')[0]['geom']

        node_sel,node_long,node_lat = self.centerline_to_node_coordinates(center)
        
        # Make a copy of original depth data and update 
        self.grid.add_node_field('node_z_bed_orig',self.grid.nodes['node_z_bed'],on_exists='pass')
        
        def channel(n,c_long,c_lat):
            z_orig=self.grid.nodes['node_z_bed_orig'][n]
            if 0:
                # rectangular channel, but only make things shallower than
                # original
                if c_lat<qcm_width/2:
                    return max(z_orig,qcm_z_thalweg)
                else:
                    return z_orig
            else:
                # linear from 0 at thalweg to 1 at prescribed width
                frac=(2*c_lat/qcm_width).clip(0,1.0)
                # V-shaped channel with 0.2m of relief, center is 0.1
                # deeper than qcm, edge 0.1 m shallower.
                return max(z_orig,qcm_z_thalweg + frac*0.2 - 0.1)

        for n,c_long,c_lat in zip(node_sel,node_long,node_lat):
            self.grid.nodes['node_z_bed'][n]=channel(n,c_long,c_lat)

        # stats on the difference:
        n_below=np.sum( self.grid.nodes['node_z_bed']<self.grid.nodes['node_z_bed_orig'])
        n_above=np.sum( self.grid.nodes['node_z_bed']>self.grid.nodes['node_z_bed_orig'])
        n_equal=np.sum( self.grid.nodes['node_z_bed']==self.grid.nodes['node_z_bed_orig'])
        # print(f"{n_below} nodes were lowered, {n_above} nodes were raised, {n_equal} nodes stayed the same")
        
        if plot: 
            fig=plt.figure(1)
            fig.clf()
            self.grid.plot_edges(color='k',lw=0.4)
            self.grid.plot_nodes(mask=node_sel)

            plot_wkb.plot_wkb(center,color='orange')

            #plt.scatter(pnts[:,0],pnts[:,1],30,node_lat,cmap=turbo)
            self.grid.contourf_node_values(self.grid.nodes['node_z_bed'],np.linspace(0,2.5,30),cmap=turbo)

            plt.axis('tight')
            plt.axis('equal')
            plt.axis('off')
            plt.axis((552070., 552178., 4124574., 4124708.))
            fig.savefig('mouth_bathy.png',dpi=150)

    # If not None, set bed elevation "near" mouth structures to the given
    # elevation
    mouth_z_dredge=None
    def add_mouth_as_structures(self,plot=False):
        """
        Use 'mouth_centerline' and 'mmouth...' features in the shapefiles
        to define many rows of structures. Each line is broken into individual
        edges, each of which gets its own structure and timeseries.
        """
        # Choose geometry from the start of the period:
        center=self.match_gazetteer(name='mouth_centerline')[0]['geom']

        # Now just pull from shapefile:
        mstructs=self.match_gazetteer(type='multistructure',name=re.compile('mmouth.*'))

        edge_mask=[] # list of indexes, not really a 'mask'
        for mstruct in mstructs:
            edge_mask.extend( self.grid.select_edges_by_polyline(mstruct['geom'],boundary=False) )
        edge_mask=np.unique(edge_mask)

        j_xy=self.grid.edges_center()[edge_mask]

        # Get the streamwise/cross coordinates
        j_ll=np.zeros( (len(edge_mask),2), np.float64)
        for i,xy in enumerate(j_xy):
            pnt=geometry.Point(xy)
            j_ll[i,0]=center.project(pnt)
            j_ll[i,1]=pnt.distance(center.interpolate(j_ll[i,0]))
        
        # Edges intersected by the centerline get exactly y=0
        # to help make sure there is always conveyance
        is_thalweg=self.grid.select_edges_intersecting(center,mask=edge_mask)
        j_thalweg=is_thalweg[edge_mask]
        j_ll[j_thalweg,1]=0.0

        if plot: 
            fig=plt.figure(1)
            fig.clf()
            self.grid.plot_edges(color='0.5',lw=0.4)
            #self.grid.plot_edges(values=j_ll[:,0],mask=edge_mask,cmap=turbo,lw=2.)
            self.grid.plot_edges(values=j_ll[:,1],mask=edge_mask,cmap=turbo,lw=2.,clim=[0,30])

            plot_wkb.plot_wkb(center,color='orange')

            plt.axis('tight')
            plt.axis('equal')
            plt.axis('off')
            plt.axis((552070., 552178., 4124574., 4124708.))
            # fig.savefig('mouth_edgy_bathy.png',dpi=150)

        # Do the business -- add structures
        ds=self.prep_qcm_data()
        # subset ds to just the run
        ds=ds.isel( time=( (ds.time>=self.run_start) & (ds.time<=self.run_stop)))

        # With the slope formulation below, this avoids divide by zero.
        qcm_width=ds.w_inlet.clip(1.0)
        qcm_z_thalweg=ds.z_thalweg

        for idx,(j,ll) in enumerate(zip(edge_mask,j_ll)):
            
            if 0: # This was still too frictional
                # Try a v-shaped channel, slope set by qcm width and
                # a presumed 1m edge-of-channel relief
                crest=qcm_z_thalweg + 1.0*(ll[1])/(qcm_width/2)

            if 0:
                # Try something more like a trapezoidal channel
                l_flat=7 # half-width of the flat bottom of the trapezoid
                z_scale=1.0 # rise of the trapezoid, with the run defined by qcm_width/2
                # for small qcm_width, additionally limit the elevation to
                # physical-ish range.
                shape=(z_scale*(ll[1]-l_flat).clip(0)/(qcm_width/2)).clip(0,8.0)
                z_offset=-0.10 # additional ad hoc adjustment to qcm_z_thalweg
                crest=qcm_z_thalweg + z_offset + shape

            if 1:
                # Trapezoid, but the flat part is the full width from the QCM
                lat_flat=qcm_width/2
                lat_slope = 1.0/10 # outside the width from qcm, 1 in 10 slope
                shape=(ll[1]-lat_flat).clip(0) * lat_slope

                # And a trapezoidal longitudinal shape, flat in the middle.
                # sloping down up/downstream.
                rise=1.0
                run=(j_ll[:,0].max() - j_ll[:,0].min())/2
                
                lon_mid=np.median(j_ll[:,0]) # or the lon coord nearest the middle 
                lon_slope=rise/run
                lon_flat=8.0 # half-width of flat length along channel
                if idx==0:
                    print("Longitudinal slope is %.3f (%.2f:%.2f)"%(lon_slope,rise,run))

                # additional ad hoc adjustment to qcm_z_thalweg of -0.10, and
                # slope down away from the middle-ish point.
                z_offset=-0.10 - lon_slope*( abs(ll[0]-lon_mid )-lon_flat).clip(0)
                crest=qcm_z_thalweg + z_offset + shape
                
            if not np.all(np.isfinite(crest)):
                print("%d/%d crest values are not finite"%( (~np.isfinite(crest)).sum(),
                                                            len(crest)))
                import pdb
                pdb.set_trace()
            
            self.add_Structure(
                type='generalstructure',
                geom=self.grid.nodes['x'][self.grid.edges['nodes'][j]],
                name='mouth_%04d'%idx,
                CrestLevel=crest,	# Bed level at centre of structure (m AD)
                extraresistance=0,                   	# Extra resistance (-)
                GateOpeningWidth=100.0,                 	# Horizontal opening width between the doors (m)
            )

        if self.mouth_z_dredge is not None:
            e2c=self.grid.edge_to_cells()
            cells=np.unique(e2c[edge_mask])
            cells=cells[cells>=0]
            nodes=np.unique(self.grid.cells['nodes'][cells].ravel())
            nodes=nodes[nodes>=0]
            self.grid.nodes['node_z_bed'][nodes] = np.minimum( self.grid.nodes['node_z_bed'][nodes],
                                                               self.mouth_z_dredge)

class PescaButanoMixin(PescaButanoBaseMixin):
    """ Add realistic boundary conditions to base Pescadero model
    """
    flow_regime='impaired' # 'impaired' or 'unimpaired'
    
    def set_bcs(self):
        self.set_creek_bcs()
        self.set_mouth_bc()
        self.set_source_sink()
        # We do have air temp and relative humidity. However, at the moment
        # no insolation data, and have not implemented a heat flux model of
        # any sort.
        self.set_wind()
        
    def set_source_sink(self):
        self.set_seepage()
        self.set_overtopping()
        self.set_atmospheric_bcs()

    def set_mouth_bc(self):
        ocean_bc=self.set_mouth_stage_qcm()
        assert ocean_bc,"mouth waterlevel BC method probably should return a BC"
        
        if self.salinity:
            if self.debug_salt:
                salt_bc=32
            else:
                # ballpark value pulled from BML time series
                salt_bc=33.0
            ocean_salt=hm.ScalarBC(parent=ocean_bc,scalar='salinity',value=salt_bc)
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
        smooth it at shorter time step.
        Include SLR offset
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
        
    def set_mouth_stage_noaa(self,hsig_adjustment=True):
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

        if hsig_adjustment:
            filters=[hm.Transform(fn_da=Hsig_adjustment),
                     hm.Lowpass(cutoff_hours=2.5)]
        else:
            filters=[hm.Lowpass(cutoff_hours=2.5)]

        ocean_bc=hm.NOAAStageBC(name='ocean_bc',station=9413450,
                                filters=filters,
                                cache_dir=cache_dir)
        self.add_bcs(ocean_bc)
        return ocean_bc

    def set_creek_bcs(self):
        df=pd.read_csv(os.path.join(local_config.model_dir,"../forcing/tu_flows/TU_flows_SI.csv"),
                       parse_dates=['time'])

        def extract_da(desc):
            df_desc=df[ df.flow_desc==desc ]
            ds=xr.Dataset.from_dataframe(df_desc.loc[:,['time','flow_cms']].set_index('time'))
            return ds['flow_cms']

        if self.flow_regime=='impaired':
            da_butano=extract_da('Impaired flow Butano TIDAL')
            da_pesca =extract_da('Impaired flow Pe TIDAL')
        elif self.flow_regime=='unimpaired':
            da_butano=extract_da('Unimpaired flow Butano TIDAL')
            da_pesca =extract_da('Unimpaired flow Pe TIDAL')
        else:
            raise Exception("Expected flow regime '%s' to be impaired or unimpaired"%self.flow_regim)

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
                if self.debug_salt:
                    salt=32.0
                else:
                    salt=0.0
                ck_salt=hm.ScalarBC(parent=ck,scalar='salinity',value=salt)
                self.add_bcs([ck_salt])
            
        if self.temperature:
            for ck in [bc_butano,bc_pesca]:
                ck_temp=hm.ScalarBC(parent=ck,scalar='temperature',value=18)
                self.add_bcs([ck_temp])
    def set_seepage(self):
        ds = self.prep_qcm_data()
        seepage= ds['seepage_abs']       
        bc_seepage=hm.SourceSinkBC(name='seepage',flow=seepage,dredge_depth=None)
        self.add_bcs([bc_seepage])
        print('Setting seepage')

    def set_overtopping(self):
        
        ds = self.prep_qcm_data()
        overtopping= ds['wave_overtop']       
        bc_overtopping=hm.SourceSinkBC(name='wave_overtop',flow=overtopping,dredge_depth=None)
        self.add_bcs([bc_overtopping])

    # time shift for QCM, while we don't have QCM output for
    # the period of the BML data
    qcm_time_offset=np.timedelta64(0,'s')
            
    def add_mouth_gen_structure(self,name,crest=None,width=None):
        """
        Set up the flow control structure for the inner mouth structure
        """
        ds = self.prep_qcm_data()

        if crest is None:
            crest= ds['z_thalweg']+self.slr
        if width is None:
            width= ds['w_inlet']    

        self.add_Structure(
            type='generalstructure',
            name=name,
            
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=55,                 	# Width structure left side (m)
            CrestWidth=50,                 	    # Width structure centre (m)
            Downstream1Width=55,                 	# Width structure right side (m)
            Downstream2Width=60,                 	# Width right side of structure (m)
            Upstream2Level=0.00,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.005,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	                    # Bed level at centre of structure (m AD)
            Downstream1Level=0.00,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.00,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=0.2,                  	# Gate lower edge level (m AD)
            pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
            pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
            pos_freeweirflowcoeff=0.55,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=0.55,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                   	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=0.55,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=0.55,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=0.0,                   	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            #GateOpeningHorizontalDirection=symmetric,           	# Horizontal direction of the opening doors
            )

    def set_atmospheric_bcs(self):
        ds=self.prep_qcm_data()

        ET_mm_hr=ds['evapotr_mmhour'] # already negative!
        # negligible direct rain, just ET=negative rain
        
        precip=hm.RainfallRateBC(rainfall_rate=24*ET_mm_hr)
        self.add_bcs([precip])

    def set_wind(self):
        ds=xr.open_dataset(os.path.join(local_config.model_dir,"../forcing/wind/lagoon-met.nc"))
        # ds.time is UTC
        # ds.u_wind, ds.v_wind are in m/s.
        # ds.T is air temperature
        # ds.rh is relative humidity
        # Condense to a single DataArray
        ds['wind']=('time','xy'), np.c_[ ds.u_wind.values, ds.v_wind.values ]
        wind_bc=hm.WindBC(wind=ds.wind)
        self.add_bcs([wind_bc])
        
    ds_qcm=None
    def prep_qcm_data(self):
        '''
        Load QCM output and prepare xr dataset
        Note that self.slr is added to z_ocean, z_thalweg and z_lagoon
        '''
        if self.ds_qcm is None:
            qcm_pre2016=pd.read_csv(os.path.join(local_config.data_dir,
                                                 "ESA_QCM/ESA_draft_PescaderoQCM_output.csv"),
                                    skiprows=[0],usecols=range(14),
                                    parse_dates=['Date (PST)'])
            qcm_2016_2017=pd.read_csv(os.path.join(local_config.data_dir,
                                                   "ESA_QCM/ESA_draft_PescaderoQCM_output_4.28.2021.csv"),
                                      skiprows=[0],usecols=range(14),
                                      parse_dates=['Date (PST)'])
            # some extra rows in the csv
            qcm_pre2016=qcm_pre2016[ ~qcm_pre2016['Date (PST)'].isnull() ]
            qcm_2016_2017=qcm_2016_2017[ ~qcm_2016_2017['Date (PST)'].isnull() ]
            qcm=pd.concat([qcm_pre2016,qcm_2016_2017], sort=False)

            qcm['time']=qcm['Date (PST)'] + np.timedelta64(8,'h') + self.qcm_time_offset # Shift to UTC.

            print(f"Range of QCM data: {qcm.time.values[0]} to {qcm.time.values[-1]}")
            
            # These are both NAVD88, converted ft=>m
            # Prefer the modified data when available:
            ocean_modified=qcm['Modified Ocean Level (feet NAVD88)']
            # Otherwise the observed data.
            ocean_level=qcm['Ocean level (feet NAVD88)']
            qcm['z_ocean']=ft_to_m * ocean_modified.combine_first(ocean_level)
            
            qcm['z_thalweg']=ft_to_m * qcm['Modeled Inlet thalweg elevation (feet NAVD88)']
            qcm['z_thalweg']=np.where( np.isfinite(qcm.z_thalweg),
                                       qcm.z_thalweg, 5.0)
                          
            qcm['z_lagoon']=ft_to_m*qcm['Modeled Lagoon Level (feet NAVD88)']

            # width
            qcm['w_inlet']=ft_to_m* qcm['Modeled Inlet Width (feet)'].fillna(0)
            
            # Other Sources and Sinks: convert form ft3/s to m3/s
            qcm['seepage']= qcm['Modeled seepage'] * 0.02831685 # from ft3/s to m3/s
            qcm['seepage_abs']=qcm['seepage']*-1 # need to be in absolute values
            qcm.loc[qcm['seepage_abs'] < 0,'seepage_abs'] = 0 # removing seepage from ocean to lagoon
                       
            # Values are already negative. Negative rainfall --> evapotranspiration
            qcm['evapotr']= qcm['Modeled ET'] * 0.02831685 # ft3/s to m3/s
            # evapotr/grid_area*1000 --> m3 to mm
            # *3600 --> s to hour
            # would be better to figure out time-average wet area. This figure is the
            # total grid area.
            # Plotted the wetted area over time for a run that spanned closed and
            # open periods. Fraction wetted was around 0.85 leading up to breach.
            # Once tidal, fraction wetted was around 0.5 mean. I think it is more the
            # closed conditions that we're interested in here, so call it 0.75
            grid_area=1940000 # m2
            qcm['evapotr_mmhour']=qcm['evapotr']/(0.75*grid_area)*1000*3600
            # data already [+]            
            qcm['wave_overtop']= qcm['Modeled wave overtopping'] * 0.02831685 # from ft3/s to m3/s
            qcm['flow_inlet']=qcm['Modeled inlet flow']* 0.02831685

            for fld in ['wave_overtop','evapotr_mmhour']:
                missing=qcm[fld].isnull()
                if np.any(missing):
                    frac_null=missing.values.sum() / len(missing)
                    print(f"WARNING: filling missing {fld} data with 0.0 for {frac_null*100:.2f}% of data")
                    qcm[fld].fillna(value=0.0,inplace=True)
            
            ds=xr.Dataset.from_dataframe(qcm[ 
                ['time','z_ocean','z_thalweg','w_inlet','seepage_abs','evapotr_mmhour','wave_overtop',
                 'z_lagoon','flow_inlet']]
                .set_index('time'))

            if self.slr != 0.0:
                ds['z_lagoon']  = ds['z_lagoon']+self.slr
                ds['z_ocean']   = ds['z_ocean']+self.slr
                ds['z_thalweg'] = ds['z_thalweg']+self.slr
                
            self.ds_qcm=ds 
            
        return self.ds_qcm
        
class PescaButano(PescaButanoMixin,dfm.DFlowModel):
    pass
