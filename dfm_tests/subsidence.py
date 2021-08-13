# Simple model runs to test subsidence/uplift for Pescadero

from stompy.grid import unstructured_grid
import numpy as np
import subprocess
import os
import matplotlib.pyplot as plt
import six
import xarray as xr
from shapely import geometry
import stompy.model.delft.dflow_model as dfm
import stompy.model.delft.io as dio
import stompy.model.hydro_model as hm
from stompy.grid import unstructured_grid
from stompy.plot import plot_utils
##
six.moves.reload_module(unstructured_grid)
six.moves.reload_module(hm)
six.moves.reload_module(dfm)

dfm.DFlowModel.dfm_bin_dir="/opt/delft3dfm_2021.03/lnx64/bin/"
os.environ['LD_LIBRARY_PATH']="/opt/delft3dfm_2021.03/lnx64/lib/"

class SubsidenceTest(dfm.DFlowModel):
    run_dir='runs/subsidence'
    fig_num=2
    n_layers=0
    num_procs=1
    mpiexec="mpiexec.mpich" # works.
    
    def desc(self):
        return "Subsidence test"
    
    def __init__(self,**kw):
        super().__init__(run_start=np.datetime64("2010-01-01 00:00"),
                         run_stop =np.datetime64("2010-01-05 00:00"),
                         **kw)
        
        self.set_run_dir(self.run_dir,mode='pristine')
        g=unstructured_grid.UnstructuredGrid(max_sides=4)
        # Sort of Pescadero Lagoon-ish
        g.add_rectilinear([0,0],
                          [600,100],
                          nx=30,ny=5)
        
        # Sloping bed to better understand uplift.
        # node_z_bed=-0.5*np.ones(g.Nnodes())
        # slopes from 0.5 at x=0 to -0.5 at x=600
        node_z_bed=0.5 - 1.0*g.nodes['x'][:,0]/600.
        g.add_node_field('node_z_bed',node_z_bed)
        self.set_grid(g)
        self.set_bcs()

        self.mdu['geometry','BedLevType']=4
        
        self.config_layers()

        self.mdu['output','MapFormat']=4 # ugrid
        
        # Turn on salinity:
        self.mdu['physics','salinity']=0
        self.mdu['physics','temperature']=0

        self.mdu['physics','InitialSalinity']=15
        self.mdu['physics','Idensform']=2

        self.add_monitor_points( [ dict(geom=geometry.Point([10,50]),
                                        name='flow_end'),
                                   dict(geom=geometry.Point([10,50]),
                                        name='stage_end')] )
        
    def config_layers(self):
        self.mdu['geometry','kmx']=self.n_layers
        self.mdu['geometry','Layertype']=2 # 1: sigma, 2: z, 3: read pliz file

    def set_bcs(self):
        left=[hm.FlowBC(geom=np.array([[0,0],[0,100]]),
                        name='left',
                        flow=0.2)
              ]
        right=[hm.HarmonicStageBC(geom=np.array([[600,0],[600,100]]),
                                  name='right',
                                  # S2=(0.3,0),
                                  msl=1.0)]
        if self.mdu['physics','salinity']=='1':
            left.append( hm.ScalarBC(parent=left[0],scalar='salinity',value=0) )
            right.append( hm.ScalarBC(parent=right[0],scalar='salinity',value=32) )

        self.add_bcs(left)
        self.add_bcs(right)
        

# 00: base case, no subsidence.
# 01: hand-edit. filetype 10 not supported.
# meteo1.f90: must be curvi, arcinfo, or uniform.
#  trying for uniform, but readprovider is returning ja=0.
#  Was missing FILENAME -- now reads it.
#  N.B. need to switch bedlevtype to match pescadero runs
# subsidence02: at a glance, works okay in 2D.
model=SubsidenceTest(run_dir='runs/subsidence03',
                     n_layers=15)

## 
model.write()

class PescaBase:
    def write_forcing(self):
        super(PescaBase,self).write_forcing()
        # manually add another forcing
        with open(self.ext_force_file(),'at') as fp:
            # change this to rainfall
            txt="""
QUANTITY=bedrock_surface_elevation
FILENAME=bedrock.tim
FILETYPE=1
METHOD=1
OPERAND=O
"""
            fp.write(txt)

        bedrock=xr.DataArray([-10,-9],dims=['time'],coords=dict(time=[self.run_start,self.run_stop]))
        self.write_tim(bedrock, os.path.join(self.run_dir,"bedrock.tim"))


        

# -----

model.partition()
import shutil
try:
    shutil.copyfile(__file__, os.path.join( model.run_dir, 'script.py'))
except NameError:
    pass

import subprocess
try:
    model.run_simulation()
except subprocess.CalledProcessError as exc:
    print(exc.output.decode())
    raise

##

try:
    his_ds.close()
except NameError:
    pass
try:
    map_ds.close()
except NameError:
    pass

his_ds=xr.open_dataset(model.his_output())

# map_ds now includes 'mesh2d_mor_bl' which does vary in time.  Progress!
map_ds=xr.open_dataset(model.map_outputs()[0])
g=unstructured_grid.UnstructuredGrid.read_ugrid(map_ds)

##

plt.figure(1).clf()
g.plot_edges(color='k',lw=0.5)
g.plot_cells(values=map_ds.mesh2d_mor_bl.isel(time=-1),cmap='jet',
             clim=[-1,0.5])
#g.plot_cells(values=map_ds.mesh2d_flowelem_bl,cmap='jet')
plt.axis('equal')

##

# Side view as scatter
plt.figure(2).clf()
fig,ax=plt.subplots(num=2)
ax.axis(ymin=-1,ymax=1.5)
for tidx in range(0,map_ds.dims['time'],5):
    ax.collections=[]
    ax.lines=[]
    ax.plot( map_ds.mesh2d_face_x.values,
             map_ds.mesh2d_mor_bl.isel(time=tidx).values,
             'o',color='brown',
             label='mor_bl(time=%d)'%tidx)

    ax.plot( map_ds.mesh2d_face_x.values, map_ds.mesh2d_s1.isel(time=tidx).values,
             'bo')
    plt.pause(0.05)
#ax.legend()

# So it runs for a while, but crashes around the time the
# bed breaks through the free surface.
# bummer.
