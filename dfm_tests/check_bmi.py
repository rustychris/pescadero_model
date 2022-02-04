# Simple model runs to test feasibility of BMI, esp. with MPI
from stompy.grid import unstructured_grid, multi_ugrid
from stompy import utils
import numpy as np
import os
import matplotlib.pyplot as plt
import six
import xarray as xr
from shapely import geometry
import stompy.model.delft.dflow_model as dfm
import stompy.model.hydro_model as hm
from stompy.grid import unstructured_grid
from stompy.plot import plot_utils
##

# Hacked executable that knows where to find its own libraries
dfm.DFlowModel.dfm_bin_dir="/opt/delft3dfm_2022.02/lnx64/bin/"
# Note that it 
dfm.DFlowModel.dfm_bin_dir="/opt/delft3dfm_2022.02/lnx64/bin"
dfm.DFlowModel.mpi_bin_dir="/home/rusty/intel/oneapi/mpi/latest/bin"

if 0:
    # new dflowfm requires intel oneapi MPI libraries. Rather than trying
    # to source setvars, pull relevant env. vars here.
    # when invoking dflowfm, it's sufficient to set these vars here.
    impi="/home/rusty/intel/oneapi/mpi/2021.5.1"
    os.environ['FI_PROVIDER_PATH']=f"{impi}/libfabric/lib/prov:/usr/lib64/libfabric"
    os.environ['I_MPI_ROOT']=impi
    os.environ['LD_LIBRARY_PATH']=f"{impi}/libfabric/lib:{impi}/lib/release:{impi}/lib"
    os.environ['ONEAPI_ROOT']="/home/rusty/intel/oneapi"
if 1:
    # When running with bmi, those variables need to be set already
    assert 'I_MPI_ROOT' in os.environ
    # The rpath hack is also no use here, and it's too late in this code to modify LD_LIBRARY_PATH
    # That is probably a big ISSUE.
    # doesn't appear to help to just set rpath on the library
    #   LD_LIBRARY_PATH
    # next things to try: copy out libmetis.so and friends to a safe place I can put on LD_LIBRARY_PATH,
    # try again...
    
# for mpi, will probably need one/both of these:
# PATH="/home/rusty/intel/oneapi/mpi/2021.5.1//libfabric/bin:/home/rusty/intel/oneapi/mpi/2021.5.1//bin:

class BmiTest(dfm.DFlowModel):
    run_dir='runs/bmi00'
    fig_num=2
    n_layers=30
    L=100
    W=20
    Lcells=10
    Wcells=2
    
    def desc(self):
        return "Base BMI test"
    
    def __init__(self,**kw):
        super().__init__(**kw)
        self.set_run_dir(self.run_dir,mode='pristine')
        g=unstructured_grid.UnstructuredGrid(max_sides=4)
        g.add_rectilinear([0,0],
                          [self.L,self.W],
                          nx=1+self.Lcells,ny=1+self.Wcells)
        node_z_bed=-2*np.ones(g.Nnodes())
        # node_z_bed=-2 + ((m_gate5.grid.nodes['x'][:,0] - 50) / 50).clip(0)
        g.add_node_field('node_z_bed',node_z_bed)
        super().__init__(grid=g,
                         run_start=np.datetime64("2010-01-01 00:00"),
                         run_stop =np.datetime64("2010-01-02 00:00"),
                         **kw)
        self.set_bcs()
        self.add_monitor_sections( [ dict(geom=geometry.LineString([[50,0],[50,20]]),
                                          name='at_gate'),
                                     dict(geom=geometry.LineString([[80,0],[80,20]]),
                                          name='downstream') ] )

        self.mdu['geometry','kmx']=self.n_layers
        self.mdu['geometry','Layertype']=2 # 1: sigma, 2: z, 3: read pliz file

        # Turn on salinity:
        self.mdu['physics','salinity']=1
        # Will come back to implement a 3D IC
        self.mdu['physics','InitialSalinity']=15
        self.mdu['physics','Idensform']=2

        # Decrease imposed mixing to simplify tests
        self.mdu['physics','Vicouv']=0.0  # Uniform horizontal eddy viscosity (m2/s)
        self.mdu['physics','Dicouv']=0.0  # eddy diffusivity (m2/s)
        self.mdu['physics','Vicoww']= 1e-6  # Uniform vertical eddy viscosity (m2/s)
        self.mdu['physics','Dicoww']= 1e-6  # Uniform vertical eddy diffusivity (m2/s)

    left='open'
    right='open'
    def set_bcs(self):
        if self.left=='open':
            left=hm.StageBC(geom=np.array([[0,0],[0,20]]),
                            name='left',
                            water_level=0.0)
            left_salt=hm.ScalarBC(parent=left,scalar='salinity',value=10)
            self.add_bcs([left,left_salt])
        if self.right=='open':
            right=hm.StageBC(geom=np.array([[100,0],[100,20]]),
                             name='right',
                             water_level=-0.01)
            right_salt=hm.ScalarBC(parent=right,scalar='salinity',value=15)
            self.add_bcs([right,right_salt])
        
    def go(self):
        self.write()
        self.run_simulation()
        self.summary_plot()
        return self
        
    def summary_plot(self,num=None,time=-1):
        if num is None:
            num=self.fig_num

        if self.num_procs==1:
            map_ds=xr.open_dataset(self.map_outputs()[0])
        else:
            map_ds=multi_ugrid.MultiUgrid(self.map_outputs())
            
        # Plot freesurface
        plt.figure(num).clf()
        fig,(ax,axu,axs)=plt.subplots(3,1,num=num,sharex=True)

        cell_order=np.argsort(map_ds.FlowElem_xzw.values)
        
        ax.plot(map_ds.FlowElem_xzw.values[cell_order],
                map_ds.s1.isel(time=time).values[cell_order],
                label='s1')
        
        ax.plot(map_ds.FlowElem_xzw.values[cell_order],
                map_ds.FlowElem_bl.values[cell_order],
                label='bed')
        
        axu.plot(map_ds.FlowElem_xzw.isel(nFlowElem=cell_order).values,
                 map_ds.ucx.isel(time=time,nFlowElem=cell_order).values,
                 label='u')

        # slice of salinity:
        scal=map_ds.sa1
        scal_slc=scal.isel(time=time).values # nFlowElem x laydim
        coll=plot_utils.pad_pcolormesh( scal.FlowElem_xcc.values[cell_order],
                                        np.arange(map_ds.dims['laydim']),
                                        scal_slc[cell_order,:].T,
                                        ax=axs,cmap='jet')
        # coll.set_clim([14,25])
        plt.colorbar(coll)
        
        ax.legend(loc='upper right')
        #axu.legend(loc='upper right')
        axu.axis(ymin=0)
        map_ds.close()

        self.annotate_sections(ax)
        
        fig.text(0.05,0.99,self.desc(),va='top')
        
    def annotate_sections(self,ax):
        his_ds=xr.open_dataset(self.his_output())
        node_counts=his_ds.cross_section_geom_node_count.values
        node_idxs=np.r_[ 0, np.cumsum(node_counts) ]

        for idx,name in enumerate(his_ds['cross_section_name'].values):
            #his_ds['cross_section_name']
            nodes=slice(node_idxs[idx],node_idxs[idx+1])
            if nodes.stop==nodes.start:
                print(f"Cross section {str(name.strip())} has no nodes")
                continue
            x=np.mean( his_ds['cross_section_geom_node_coordx'].values[nodes] )
            Q=his_ds['cross_section_discharge'].isel(time=-1,cross_section=idx).item()
            U=his_ds['cross_section_velocity'].isel(time=-1,cross_section=idx).item()
            A=his_ds['cross_section_area'].isel(time=-1,cross_section=idx).item()

            ax.text(x,0,f"Q={Q:.3f}\nU={U:.3f}\nA={A:.3f}",va='top')

        txt=[]
        if 'gategens' in his_ds.dims:
            for idx in range(his_ds.dims['gategens']):
                txt.append(f"Gate {idx}")
                for name in [
                        "gategen_crest_level",
                        "gategen_crest_width",
                        "gategen_gate_lower_edge_level",
                        "gategen_flow_through_height",
                        "gategen_gate_opening_width",
                        "gategen_s1up",
                        "gategen_s1dn"]:
                    val=his_ds[name].isel(gategens=idx,time=-1).item()
                    if val>1e20:
                        val=np.nan
                    txt.append( f"  {name}={val:.3f}")
            ax.text(0.05,0.95,"\n".join(txt),transform=ax.transAxes,va='top')
            
        his_ds.close()
        

# Structure types:
class WithGate(BmiTest):
    GateHeight=5
    GateLowerEdgeLevel=-0.5
    GateOpeningWidth=0.0
    CrestLevel=-0.6
    CrestWidth=0.5
    def desc(self):
        return (f"With gate: door_height={self.GateHeight} lower_edge={self.GateLowerEdgeLevel} open_width={self.GateOpeningWidth}"
                + "\n"
                +f"  sill_level={self.CrestLevel}  sill_width={self.CrestWidth}")

    def __init__(self,**kw):
        super(WithGate,self).__init__(**kw)
        struct_kws=dict(
            type='gate', # 'generalstructure' 
            name='gate',
            GateHeight=self.GateHeight, # top of door to bottom of door
            GateLowerEdgeLevel=self.GateLowerEdgeLevel,
            GateOpeningWidth=self.GateOpeningWidth,
            CrestLevel=self.CrestLevel,
            # horizontal_opening_direction='symmetric',
            geom=np.array([[50,0],[50,20]]),
            CrestWidth=self.CrestWidth
            )
        self.add_Structure(**struct_kws)


class WithSrcSink(WithGate):
    GateLowerEdgeLevel=-0.5
    CrestLevel=-0.5
    
    z_left=-1.5
    z_right=-1.6
    left='open'
    right='closed'

    Q_src_sink=0.00
    
    def desc(self):
        return f"Src/sink: z_left={self.z_left} z_right={self.z_right} Q={self.Q_src_sink}"

    def __init__(self,**kw):
        super(WithSrcSink,self).__init__(**kw)

    def set_bcs(self):
        super(WithSrcSink,self).set_bcs()

        src_sink=hm.SourceSinkBC(name='src_sink',
                                 z=-2.0,
                                 geom=np.array([ [45,10],
                                                 [55,10] ]),
                                 flow=self.Q_src_sink)
        src_sink_salt=hm.ScalarBC(parent=src_sink,
                                  scalar='salinity',
                                  value=0) #value here will add salt
        
        src_sink_return=hm.SourceSinkBC(name='sink_src',
                                        geom=np.array([ [45,10,5],
                                                        [55,10,5] ]),
                                        flow=-self.Q_src_sink)

        self.add_bcs([src_sink,src_sink_salt,src_sink_return])

model=WithSrcSink( GateLowerEdgeLevel=-2.0,CrestLevel=-2.0,fig_num=6,
                   Q_src_sink=0.0,
                   Lcells=20,Wcells=6,
                   num_procs=1,
                   CrestWidth=0.5)

model.write()
model.partition()


## 
model.run_simulation()
model.summary_plot()

## 
for t in range(50):
    m_gate_bed.summary_plot(time=t)
    plt.draw()
    plt.pause(0.01)

##

# Ideally scan the src/sinks, somehow annotate if it's a source-sink that is "online"
# and get the coordinates from the src/sink.


## 

# Can run a src/sink test case that looks reasonable
# So I can load the model via BMI, serial.

# Next: Then try to control src/sink with BMI.

# Now try things with BMI:
from stompy import utils
import bmi.wrapper
from numpy.ctypeslib import ndpointer  # nd arrays
from ctypes import (
    # Types
    c_double, c_int, c_char_p, c_bool, c_char, c_float, c_void_p,
    # Complex types
    # ARRAY, Structure,
    # Making strings
    # Pointering
    POINTER, byref, # CFUNCTYPE,
    # Loading
    # cdll
)

sim=bmi.wrapper.BMIWrapper(engine="/opt/delft3dfm_2022.02/lnx64/lib-safe/libdflowfm.so")
sim.initialize('runs/bmi00/flowfm.mdu')

@utils.add_to(sim)
def get_scalar_double(self,name):
    """
    Read a scalar double. DFM seems not to handle some of the type/shape/rank
    queries, so here we force it.
    Return value is a numpy scalar -- for updating, modify this and pass back
    to set_var
    """ 
    c_name = bmi.wrapper.create_string_buffer(name)
    get_var = self.library.get_var
    rank=0
    shape=()
    arraytype = ndpointer(dtype="double",
                          ndim=rank,
                          shape=shape,
                          flags='F')

    get_var.argtypes = [c_char_p, POINTER(arraytype)]
    get_var.restype = None
    data = arraytype()
    # Get the array
    get_var(c_name, byref(data))
    array=data.contents 
    return array

##

# Test retrieving cell locations and freesurface.
sim.update(300)

# cell centers
xz=sim.get_var('xz')
yz=sim.get_var('yz')

s1=sim.get_var('s1')
hs=sim.get_var('hs') # waterdepth

# HERE:
#  assuming I keep going on the file-based communication, then
#  need a way for processors to know what coordinates to look
#  for.
#  And how to communicate results back without causing a race condition.
#  Might be worth just trying this out on farm and seeing (a) does 
#  everything work so far? (b) how hard is it to get a mpipy
#  integrated?

## 
# sim.get_time_step() # DtUser = 300s
# This had worked, but now I'm getting "NULL pointer access."
# seems to work if I run the model above first...
Qsrc_sink=sim.get_scalar_double('sourcesinks/src_sink/discharge')
Qsrc_sink[()]=0.1 # easiest to just overwrite the returned value and pass it back
sim.set_var('sourcesinks/src_sink/discharge',Qsrc_sink)

#Qsink_src=sim.get_scalar_double('sourcesinks/sink_src/discharge')
#Qsink_src[()]=0.0 # easiest to just overwrite the returned value and pass it back
#sim.set_var('sourcesinks/sink_src/discharge',Qsrc_sink)

## 
# simulate half a day:
# this seems to keep just returning 0.0.
dt=300.0
while sim.get_current_time()<sim.get_end_time():
    sim.update(dt)
    Qsrc_sink=sim.get_scalar_double('sourcesinks/src_sink/discharge')
    print(Qsrc_sink)

sim.finalize()


