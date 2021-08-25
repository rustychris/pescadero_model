"""
Runs targeting the 2016/2017 period of the BML field data.
Here focused on 2D runs and how various mouth treatments alter
the stage results.
"""
import matplotlib
#matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pesca_base
import os
import shutil
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy import utils
from stompy.grid import unstructured_grid
import stompy.plot.cmap as scmap
turbo=scmap.load_gradient('turbo.cpt')
from stompy.plot import plot_wkb
from shapely import ops, geometry
import re

import six
six.moves.reload_module(unstructured_grid)
six.moves.reload_module(hydro_model)
six.moves.reload_module(dflow_model)
six.moves.reload_module(pesca_base)


##
class PescaMouthy(pesca_base.PescaButano):
    pillars=False

    # Note that the salinity runs have been dropping the thalweg by 0.15 cm
    def add_mouth_structure(self):
        # Baseline:
        super(PescaMouthy,self).add_mouth_structure()

        # synthetic DEM instead of structures
        #self.add_mouth_as_bathy()

        # synthetic DEM as structures
        # self.add_mouth_as_structures()

        # Make a sequence of partially open gates?  nah

        # manually added some pillars, and now just one mouth structure
        #self.add_mouth_gen_structure(name='mouth_in')
        self.add_pillars()

    pillar_fn='pillars.pliz'
    def add_pillars(self):
        if self.pillars:
            self.mdu['geometry','PillarFile'] = self.pillar_fn
    def write_pillars(self):
        pillar_text="""\
pillars
   9  4
552092 4124623 5 2.5
552096 4124624 5 2.5
552099 4124626 5 2.5
552103 4124628 5 2.5
552106 4124629 5 2.5
552109 4124631 5 2.5
552112 4124632 5 2.5
552114 4124633 5 2.5
552118 4124635 5 2.5
"""
        with open(os.path.join(self.run_dir,self.pillar_fn),'wt') as fp:
            fp.write(pillar_text)

    def write_forcing(self):
        super(PescaMouthy,self).write_forcing()
        if self.pillars:
            self.write_pillars()

    def centerline_to_node_coordinates(self,center,max_width=50.0):
        """
        center: linestring geometry
        max_width: full width of the swath to consider
        returns node_indexes, d_along, d_across
        node_indexes is in sorted order.

        Select nodes within max_width/2 of the centerline, 
        and approximate an along/across channel coordinate system.
        Trims the ends to approximate the distance as perpendicular to the
        line.
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
            
    def add_mouth_as_structures(self,plot=False):
        # Some of this is the same as add_mouth_as_bathy()
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

        qcm_width=ds.w_inlet
        qcm_z_thalweg=ds.z_thalweg

        for idx,(j,ll) in enumerate(zip(edge_mask,j_ll)):
            # Try a v-shaped channel, slope set by qcm width and
            # a presumed 1m edge-of-channel relief

            # This was still too frictional
            # crest=qcm_z_thalweg + 1.0*(ll[1])/(qcm_width/2)

            # Open conditions: 
            # Try something more like a trapezoidal channel
            l_flat=7 # half-width of the flat bottom
            z_scale=1.0
            z_offset=-0.10
            # 0.001 avoids division by zero when closed
            crest=( qcm_z_thalweg
                    + z_offset
                    + z_scale*max(0,(ll[1]-l_flat))
                      /np.maximum(0.001,qcm_width/2)
                  )
            # In closed conditions revert to constant structure elevation
            closed=qcm_width==0
            crest.loc[closed]=qcm_z_thalweg.loc[closed]
            assert np.all(np.isfinite(crest.values))
            
            self.add_Structure(
                type='generalstructure',
                geom=self.grid.nodes['x'][self.grid.edges['nodes'][j]],
                name='mouth_%04d'%idx,
                CrestLevel=crest,	# Bed level at centre of structure (m AD)
                extraresistance=0,                   	# Extra resistance (-)
                GateOpeningWidth=100.0,                 	# Horizontal opening width between the doors (m)
            )        
            
model=PescaMouthy(run_start=np.datetime64("2016-06-14 00:00"),
                  run_stop=np.datetime64("2016-06-23 00:00"),
                  #run_start=np.datetime64("2016-12-10 00:00"),
                  #run_stop=np.datetime64("2016-12-20 00:00"),
                  run_dir="data_mouth_v015",
                  salinity=False,
                  temperature=False,
                  nlayers_3d=0,
                  pch_area=2.0)

model.mdu['output','MapInterval']=1800
# model.mdu['time','DtUser']=30.
# model.mdu['numerics','CFLmax']=0.4
# model.mdu['time','AutoTimestepNoStruct']=1

## 
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

# v001: flat synthetic bed in there...
# v002: oops, only adjusted levels for one of the mouth structures.  this remedies it
# v003: linear channel profile
# v004: change extra resistance from 4 to 1
# v005: manually add pillars.  too small, little change
# v006: big pillars. Decent improvement?
# v007: big pillars, drop the second mouth structure.
# v008: switch to bedlevel=5 to be consistent with 3D, should be comparable to 3D v114.
# v009: mimic salt run v116. is 2D still super different?
# v010: wacky structures
# v011: wacky structures, no extraresistance
# v012: wacky structures, trapezoidish
# v013: slightly narrower channel, offset down
# v014: shift the start/stop a bit later to test for spinup effects
# v015: back to v013 period, a bit longer, and use new bathy 20210820
# v016: winter breach period with mouth_as_structures. Fails during the breach 
# v017: winter breach, back to two structures with resistance (like salt v116)
# v018: longer period like v015, but with the mouth structures.
#     appears to be identical to v015.

