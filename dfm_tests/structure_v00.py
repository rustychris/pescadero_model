# Simple model runs to test flow control structures
from stompy.grid import unstructured_grid
import numpy as np
import os
import matplotlib.pyplot as plt
import six
import xarray as xr
import stompy.model.delft.dflow_model as dfm

##
six.moves.reload_module(dfm)
dfm.DFlowModel.dfm_bin_dir="/home/rusty/src/dfm/1.6.1/lnx64/bin" 
os.environ['LD_LIBRARY_PATH']="/home/rusty/src/dfm/1.6.1/lnx64/lib/"


class StructureTest(dfm.DFlowModel):
    run_dir='runs/open'
    fig_num=2
    def __init__(self,**kw):
        self.set_run_dir(self.run_dir,mode='pristine')
        g=unstructured_grid.UnstructuredGrid(max_sides=4)
        g.add_rectilinear([0,0],
                          [100,20],
                          nx=11,ny=2)
        g.add_node_field('node_z_bed',-2*np.ones(g.Nnodes()))
        super(StructureTest,self).__init__(grid=g,
                                           run_start=np.datetime64("2010-01-01 00:00"),
                                           run_stop =np.datetime64("2010-01-02 00:00"),
                                           **kw)
        self.set_bcs()
    def set_bcs(self):
        self.add_bcs([ dfm.StageBC(geom=np.array([[0,0],[0,20]]),
                                   name='left',
                                   z=0.0),
                       dfm.StageBC(geom=np.array([[100,0],[100,20]]),
                                   name='right',
                                   z=-0.01)])
    def go(self):
        self.write()
        self.run_simulation()
        self.summary_plot()
        return self
        
    def summary_plot(self,num=None):
        if num is None:
            num=self.fig_num
            
        map_ds=xr.open_dataset(self.map_outputs()[0])
        # Plot freesurface
        plt.figure(num).clf()
        fig,(ax,axu)=plt.subplots(2,1,num=num,sharex=True)

        ax.plot(map_ds.FlowElem_xzw,map_ds.s1.isel(time=-1).values,label='s1')
        ax.plot(map_ds.FlowElem_xzw,map_ds.FlowElem_bl.values,label='bed')
        axu.plot(map_ds.FlowElem_xzw,map_ds.ucx.isel(time=-1).values,label='u')
        ax.legend(loc='upper right')
        axu.legend(loc='upper right')
        axu.axis(ymin=0)
        map_ds.close()

# Structure types:
class WithGate(StructureTest):
    door_height=5
    lower_edge_level=-0.5
    opening_width=0.5
    sill_level=-0.6
    sill_width=None
    
    def __init__(self,**kw):
        super(WithGate,self).__init__(**kw)
        struct_kws=dict(
            type='gate',
            name='gate',
            door_height=self.door_height, # top of door to bottom of door
            lower_edge_level=self.lower_edge_level,
            opening_width=self.opening_width,
            sill_level=self.sill_level,
            horizontal_opening_direction='symmetric',
            geom=np.array([[50,0],[50,20]])
            )
        if self.sill_width is not None:
            struct_kws['sill_width']=self.sill_width
        self.add_Structure(**struct_kws)
        
#m_base=StructureTest().go()
m_gate=WithGate().go()

# sill_width seems to do nothing, at least when opening_width is specified
#m_gate2=WithGate(sill_width=0.2,fig_num=3).go()

# opening_width does make a difference, even in this case where the gate
# spans a single computational edge.
m_gate3=WithGate(opening_width=7.0,fig_num=4).go()

# HERE:
# Test the above in 3D.
# Does it properly route the right density through?

