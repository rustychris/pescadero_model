# Simple model runs to test layering for Pescadero
#  - vertpliz attempts crash.
#  - also test turbulence, mixing.

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
six.moves.reload_module(hm)
six.moves.reload_module(dfm)

dfm.DFlowModel.dfm_bin_dir="/opt/delft3dfm_2021.03/lnx64/bin/"
os.environ['LD_LIBRARY_PATH']="/opt/delft3dfm_2021.03/lnx64/lib/"

class VertPlizTest(dfm.DFlowModel):
    run_dir='runs/vertpliz'
    fig_num=2
    n_layers=25
    num_procs=4
    # mpiexec="mpiexec.openmpi" # seems to just run 4 copies
    mpiexec="mpiexec.mpich" # works.
    
    def desc(self):
        return "Vert pliz test"
    
    def __init__(self,**kw):
        self.set_run_dir(self.run_dir,mode='pristine')
        g=unstructured_grid.UnstructuredGrid(max_sides=4)
        # Sort of Pescadero Lagoon-ish
        g.add_rectilinear([0,0],
                          [600,100],
                          nx=60,ny=5)
        node_z_bed=-0.5*np.ones(g.Nnodes())
        g.add_node_field('node_z_bed',node_z_bed)
        super().__init__(grid=g,
                         run_start=np.datetime64("2010-01-01 00:00"),
                         run_stop =np.datetime64("2010-01-03 00:00"),
                         **kw)
        self.set_bcs()

        self.config_layers()

        self.mdu['output','MapFormat']=4 # ugrid
        
        # Turn on salinity:
        self.mdu['physics','salinity']=1
        self.mdu['physics','temperature']=0

        self.mdu['physics','InitialSalinity']=15
        self.mdu['physics','Idensform']=2

        self.add_monitor_points( [ dict(geom=geometry.Point([10,50]),
                                        name='flow_end'),
                                   dict(geom=geometry.Point([10,50]),
                                        name='stage_end')] )
        # Decrease imposed mixing to simplify tests
        # self.mdu['physics','Vicouv']=0.0  # Uniform horizontal eddy viscosity (m2/s)
        # self.mdu['physics','Dicouv']=0.0  # eddy diffusivity (m2/s)
        # self.mdu['physics','Vicoww']= 1e-6  # Uniform vertical eddy viscosity (m2/s)
        # self.mdu['physics','Dicoww']= 1e-6  # Uniform vertical eddy diffusivity (m2/s)
        
    def config_layers(self):
        self.mdu['geometry','kmx']=self.n_layers
        self.mdu['geometry','Layertype']=2 # 1: sigma, 2: z, 3: read pliz file

    def set_bcs(self):
        left=hm.FlowBC(geom=np.array([[0,0],[0,100]]),
                       name='left',
                       flow=0.2)
        left_salt=hm.ScalarBC(parent=left,scalar='salinity',value=0)
        self.add_bcs([left,left_salt])
        
        right=hm.HarmonicStageBC(geom=np.array([[600,0],[600,100]]),
                                 name='right',
                                 S2=(0.3,0),
                                 msl=1.0)
        
        right_salt=hm.ScalarBC(parent=right,scalar='salinity',value=32)
        self.add_bcs([right,right_salt])
        

# 00: starting point.
# 01: try alternate vertical advection.  Difference of maybe 0.1ppt?
# 02: include Forester=20. This increases near-bed salinity by about 0.4 ppt.
# I guess that's something?
# 03: explicit -- looks identicaly to central implicit
# 04: regular advection, but constant turbulence
# 05: regular adv+turb, but dial down dicoww to 0
# 06: regular adv+turb, but dial down dicoww to 1e-10

# 07: Vertadvtypsal=4, forester=20, dicoww=1e-10, turb_model=3
#   This had some twitchiness, and was considerably fresher than 8.
# 08: Vertadvtypsal=6, forester=20, dicoww=1e-10, turb_model=3
# 09: Vertadvtypsal=2, forester=20, dicoww=1e-10, turb_model=3
# 10: Vertadvtypsal=6, forester=0, dicoww=1e-10, turb_model=3
#   Compared to 8, this is slightly fresher near the bed

# Question: with dicoww=1e-10, and Forester=20, is there a difference
# between default VertAdv and 2, and 4?  Which is faster between 2 and 4?
model=VertPlizTest(run_dir='runs/vertpliz10')
model.mdu['numerics','Vertadvtypsal']=6 #
model.mdu['numerics','Maxitverticalforestersal']=0 # Forester
model.mdu['numerics','Turbulencemodel']=3
# model.mdu['physics','vicoww']=5e-5
# So it does make a difference whether dicoww is 0.0 or the default.
# what about just a real small value?
model.mdu['physics','dicoww']=1e-10

model.write()
model.partition()
import shutil
shutil.copyfile(__file__, os.path.join( model.run_dir, 'script.py'))

import subprocess
try:
    model.run_simulation()
except subprocess.CalledProcessError as exc:
    print(exc.output.decode())
    raise



##

class VariablePliz(VertPlizTest):
    """ 
    Fails
    """
    def config_layers(self):
        self.mdu['geometry','kmx']=self.n_layers
        self.mdu['geometry','Layertype']=3
        fn='vertlayers.pliz'
        self.mdu['geometry','VertplizFile']=fn

        # My understanding is that the first 'z' coordinate is actually
        # the number of layers,
        # and the second 'z' coordinate is the layertype, and all z
        # values beyond  that are ignored.
        pli_data=[ ('domain',
                    np.array( [ [-15,-5,10],
                                [605,-5,2],
                                [605,105,2],
                                [-5,105,10] ] )) ]

        dio.write_pli(os.path.join(self.run_dir,fn),
                      pli_data)
        
