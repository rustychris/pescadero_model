"""
2D runs with a truncated domain for fast testing
of mouth parameters
"""
import matplotlib
#matplotlib.use('Agg')
from shapely import ops

import matplotlib.pyplot as plt
import pesca_base
import os
import shutil
import numpy as np
from stompy.model import hydro_model
#from stompy.model.delft import dflow_model
import stompy.model.hydro_model as hm
from stompy import utils
from stompy.grid import unstructured_grid
import stompy.plot.cmap as scmap
turbo=scmap.load_gradient('turbo.cpt')
from stompy.plot import plot_wkb
from shapely import ops, geometry
import re

import six
six.moves.reload_module(pesca_base)

##
class PescaShort(pesca_base.PescaButano):
    num_procs=4
    salinity=False
    temperature=False
    nlayers_3d=0
    # mouth_z_dredge=0,
    pch_area=2.0
    run_start=np.datetime64("2016-12-10 00:00")
    run_stop=np.datetime64("2016-12-10 06:00")

    clip_to_right=np.array( [
        [552193.5, 4124460.1],
        [552221.0, 4124478.6],
        [552284.7, 4124521.4],
        [552306.3, 4124560.1],
        [552304.9, 4124570.9],
        [552245.0, 4124608.2]
    ])
    
    def set_grid(self,grid_fn):
        onlymouth_fn=os.path.join( os.path.dirname(grid_fn), "onlymouth.nc")
        
        if utils.is_stale(onlymouth_fn,[grid_fn]):
            print("Will generate mouth-only grid")
            # And clip:
            grid=unstructured_grid.UnstructuredGrid.read_ugrid(grid_fn)
            cell_mask=grid.select_cells_by_cut(geometry.LineString(self.clip_to_right))

            for c in np.nonzero(~cell_mask)[0]:
                grid.delete_cell(c)

            grid.delete_orphan_edges()
            grid.delete_orphan_nodes()
            grid.renumber()
            grid.write_ugrid(onlymouth_fn)
        else:
            print("Will use cached mouth-only grid, %s"%onlymouth_fn)
            grid=unstructured_grid.UnstructuredGrid.read_ugrid(onlymouth_fn)
        super(PescaShort,self).set_grid(grid)

    def set_bcs(self):
        # Skip creek, atmospheric bcs.
        self.set_mouth_bc()
        self.set_lagoon_bc()

    flow=20.0
    def set_lagoon_bc(self):
        """
        Use the interpolated QCM waterlevel datas as BC.
        Stock QCM output is a bit coarse (dt=1h) for stage, so 
        smooth it at shorter time step
        """
        ds=self.prep_qcm_data()
        pesca_bc=hm.FlowBC(name='QLagoon',
                           flow=self.flow, # ds['flow_inlet'],
                           geom=self.clip_to_right)
        
        self.add_bcs([pesca_bc])
        return pesca_bc

    # self.add_monitoring() # leave as is
    # self.set_friction() leave as is
    def add_structures(self):
        # omit other structures
        self.add_mouth_structure()

    def set_mouth_stage_qcm(self):
        """
        Use the interpolated QCM waterlevel datas as BC.
        Stock QCM output is a bit coarse (dt=1h) for stage, so 
        smooth it at shorter time step
        """
        ocean_bc=hm.StageBC(name='ocean_bc',water_level=0.0)
        self.add_bcs([ocean_bc])
        return ocean_bc
        
    def add_mouth_structure(self):
        self.add_mouth_gen_structure(name='mouth_in',crest=self.crest,width=50.0)
        #self.add_mouth_as_bathy(crest=self.crest,width=50.0)

    crest=0.8
    extraresistance=0.0
    coeff=1.0
    def add_mouth_gen_structure(self,name,crest=None,width=None):
        """
        Set up the flow control structure for the inner mouth structure
        """
        ds = self.prep_qcm_data()

        if crest is None:
            crest= ds['z_thalweg']
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
            pos_freeweirflowcoeff=self.coeff,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=self.coeff,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                   	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=self.coeff,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=self.coeff,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=self.extraresistance,     	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            #GateOpeningHorizontalDirection=symmetric,           	# Horizontal direction of the opening doors
            )

    # Newer version
    def add_mouth_as_bathy(self,crest=0.5,width=50.0,plot=True):
        """
        Update bed elevation in the grid to reflect the QCM geometry
        at a specific time (run_start). Uses the 'mouth_centerline' feature
        in the shapefile inputs to define the centerline and which nodes will
        be updated. Bed is static, though.
        """
        center=self.match_gazetteer(name='mouth_centerline')[0]['geom']
        node_sel,node_long,node_lat = self.centerline_to_node_coordinates(center)
        # Make a copy of original depth data and update 
        self.grid.add_node_field('node_z_bed_orig',self.grid.nodes['node_z_bed'],on_exists='pass')
        
        def channel(n,c_long,c_lat):
            # from mouth_as_structure:
            # Trapezoid, but the flat part is the full width from the QCM
            lat_slope = 1.0/10 # outside the width rise with 1:10 slope
            lat_shape=(c_lat-width/2).clip(0) * lat_slope

            # And a trapezoidal longitudinal shape, flat in the middle.
            # sloping down up/downstream.
            rise=1.0
            run=(c_long.max() - c_long.min())/2
                
            lon_mid=np.median(c_long) # or the lon coord nearest the middle 
            lon_slope=rise/run
            lon_flat=10.0 # half-width of flat length along channel

            print("Longitudinal slope is %.3f (%.2f:%.2f)"%(lon_slope,rise,run))

            # additional ad hoc adjustment to qcm_z_thalweg of -0.10, and
            # slope down away from the middle-ish point.
            lon_shape= -lon_slope* (abs(c_long-lon_mid)-lon_flat).clip(0)
            
            z_node=crest + lon_shape + lat_shape
            z_orig=self.grid.nodes['node_z_bed_orig'][n]
            return np.maximum(z_orig,z_node)

        self.grid.nodes['node_z_bed'][node_sel] = channel(node_sel,
                                                          node_long,
                                                          node_lat)
        
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

flow=10
crest=0.40

if flow==20:
    # For this specific case it take extra=10 just to get back to the same
    # friction as extra=0
    
    #extra=20.0 # spot on
    #coeff=1.0
    
    #extra=5.0 # maybe coeff needs to be 0.47
    #coeff=0.5 

    extra=0.0  # spot on
    coeff=0.55

if flow==10:
    extra=0.0  
    coeff=0.50
    
if flow==5:
    #extra=40.0 # still shy
    #coeff=1.0
    
    #extra=40.0 # still shy
    #coeff=0.5 

    extra=0.0  
    coeff=0.55
    

model=PescaShort(run_dir="data_onlymouth_v043_z%.2f_Q%03.0f_ex%g_co%g"%(crest,flow,extra,coeff),
                 flow=flow,extraresistance=extra,crest=crest,coeff=coeff)

model.mdu['output','MapInterval']=1800
model.mdu['geometry','ChangeVelocityAtStructures']=1
model.mdu['numerics','CFLmax']=0.5
model.mdu['numerics','Teta0']=0.7

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

# v032: base. free weir coefficient=10
# v033: free weir coefficient=1
# v034: structure up to 0.8 for better match
# v035:  *now* try free weir coeffs of 10
# v036:  and larger drowned weir coeff
# v037:  now greater flow, to 40 m3/s

# v038: suite of runs testing extraresistance
# v039: suite of runs testing structure height, extra=0
# v040: suite of runs testing structure height, extra=1.0
# v041: suite of runs testing structure height, extra=3.0
# v042: suite of runs testing mouth_as_bathy() ~ fn(crest, Q)
