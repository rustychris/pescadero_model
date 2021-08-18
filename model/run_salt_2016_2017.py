"""
Runs targeting the 2016/2017 period of the BML field data
"""
import pesca_base
import os
import shutil
import numpy as np
from stompy import utils
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid
import shapely
if shapely.__version__ < "1.7.":
    print("WARNING: shapely before 1.7 lacks substring(), which is used in the synthetic bathymetry")
from shapely import ops, geometry

##
class PescaDeeper(pesca_base.PescaButano):
    pillars=False

    def update_initial_water_level(self):
        # stand-in while Sophie updates
        super(pesca_base.PescaButanoBase,self).update_initial_water_level()

    def add_mouth_structure(self):
        # Baseline:
        super(PescaDeeper,self).add_mouth_structure()

        # synthetic DEM instead of structures
        # self.add_mouth_as_bathy()

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
        super(PescaDeeper,self).write_forcing()
        if self.pillars:
            self.write_pillars()

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
            fig.savefig('mouth_bathy.png',dpi=150)
        

model=PescaDeeper(run_start=np.datetime64("2016-06-10 00:00"),
                  run_stop=np.datetime64("2016-06-20 00:00"),
                  run_dir="run_salt_20160520-v116",
                  salinity=True,
                  temperature=False,
                  nlayers_3d=100,
                  pch_area=2.0,
                  z_max=2.5,
                  z_min=-0.5,
                  num_procs=16)

# model.mdu['time','AutoTimestep']=2 # 5=bad. 4 okay but slower, seems no better than 2.
model.mdu['output','MapInterval']=12*3600

model.mdu['numerics','TurbulenceModel']=3 # 0: breaks, 1: constant,  3: k-eps
model.mdu['physics','Dicoww']=1e-8
model.mdu['physics','Vicoww']=1e-7

#model.mdu['numerics','Vertadvtypsal']=4
#model.mdu['numerics','Maxitverticalforestersal']=20
model.mdu['numerics','CFLmax']=0.4

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

