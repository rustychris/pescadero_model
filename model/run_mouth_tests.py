"""
Runs targeting the 2016/2017 period of the BML field data.
Here focused on 2D runs and how various mouth treatments alter
the stage results.
"""
import pesca_base
import os
import shutil
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy import utils
from stompy.grid import unstructured_grid
from shapely import ops, geometry

##
class PescaMouthy(pesca_base.PescaButano):
    # Note that the salinity runs have been dropping the thalweg by 0.15 cm
    def update_initial_water_level(self):
        # stand-in while Sophie updates
        super(pesca_base.PescaButanoBase,self).update_initial_water_level()

    def add_mouth_structure(self):
        # Baseline:
        # super(PescaMouth,self).add_mouth_structure()
        # Will add in DEM update here:
        self.add_mouth_as_bathy()

    def add_mouth_as_bathy(self,plot=False):
        # Choose geometry from the start of the period:
        ds=self.prep_qcm_data()
        sel=np.nonzero( ds.time.values>=self.run_start )[0][0]
        qcm_snap=ds.isel(time=sel)
        qcm_width=qcm_snap.w_inlet.item()
        qcm_z_thalweg=qcm_snap.z_thalweg.item()

        # Use thalweg_pesc to guide the center of the synthetic channel
        thalweg_line=self.match_gazetteer(name='thalweg_pesc')[0]['geom']
        bound_down=self.match_gazetteer(name='mouth_out')[0]['geom']
        bound_up  =self.match_gazetteer(name='mouth_in')[0]['geom']
        max_width=50.0

        # Trim the thalweg based on the bounds
        dists =[ thalweg_line.project(thalweg_line.intersection(b))
                 for b in [bound_down,bound_up]]
        
        # could pad out...
        center=ops.substring(thalweg_line,dists[0],dists[1])

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
        node_lat=utils.dist(projected-pnts) # Not a true coordinate, since it's nonnegative

        good=node_lat<=max_width/2.
        node_sel=node_sel[good]
        node_long=node_long[good]
        node_lat=node_lat[good]
        pnts=self.grid.nodes['x'][node_sel]
        # Now I have a local coordinate system (ish)

        # Make a copy of original depth data and update 
        self.grid.add_node_field('node_z_bed_orig',self.grid.nodes['node_z_bed'],on_exists='pass')
        
        def channel(n,c_long,c_lat):
            # rectangular channel, but only make things shallower than
            # original
            z_orig=self.grid.nodes['node_z_bed_orig'][n]
            if c_lat<qcm_width/2:
                return max(z_orig,qcm_z_thalweg)
            else:
                return z_orig

        for n,c_long,c_lat in zip(node_sel,node_long,node_lat):
            self.grid.nodes['node_z_bed'][n]=channel(n,c_long,c_lat)

        if plot: 
            plt.figure(1).clf()
            self.grid.plot_edges(color='k',lw=0.4)
            self.grid.plot_nodes(mask=node_sel)

            plot_wkb.plot_wkb(thalweg_line,color='g')
            for b in [bound_down,bound_up]:
                plot_wkb.plot_wkb(b,color='r')
            plot_wkb.plot_wkb(center,color='orange')

            #plt.scatter(pnts[:,0],pnts[:,1],30,node_lat,cmap=turbo)
            self.grid.contourf_node_values(self.grid.nodes['node_z_bed'],np.linspace(0,2.5,30),cmap=turbo)

            plt.axis('tight')
            plt.axis('equal')
            plt.axis('off')
            plt.axis((552070., 552178., 4124574., 4124708.))

    
model=PescaMouthy(run_start=np.datetime64("2016-06-14 00:00"),
                  run_stop=np.datetime64("2016-06-18 00:00"),
                  run_dir="run_mouth_v001",
                  salinity=False,
                  temperature=False,
                  nlayers_3d=0,
                  pch_area=2.0,
                  num_procs=4)


## 
model.mdu['output','MapInterval']=1800
#model.mdu['numerics','CFLmax']=0.4

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

# v000:
# Getting a segfault. Happens the same for serial or mpi. Traceback mentions
# setdt, setdtorg.
# Clearing conda doesn't help.
# Occurs for 2021.03 *and* my local compile, appears to be same location.
# Related to timestepping options I had for 3D.  Moved those to config_layers(),
# Now running okay.
# Not *super* fast, though.  Maybe 1h for the whole thing?

