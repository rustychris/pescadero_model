# Simple model runs to test flow control structures
from stompy.grid import unstructured_grid
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
six.moves.reload_module(unstructured_grid)
six.moves.reload_module(hm)
six.moves.reload_module(dfm)

dfm.DFlowModel.dfm_bin_dir="/opt/delft3dfm_2021.01/lnx64/bin/"
os.environ['LD_LIBRARY_PATH']="/opt/delft3dfm_2021.01/lnx64/lib/"

# dfm.DFlowModel.dfm_bin_dir="/home/rusty/src/dfm/1.6.3/lnx64/bin" 
# os.environ['LD_LIBRARY_PATH']="/home/rusty/src/dfm/1.6.3/lnx64/lib/"

class StructureTest(dfm.DFlowModel):
    run_dir='runs/open'
    fig_num=2
    n_layers=30
    
    def desc(self):
        return "Base structure test"
    
    def __init__(self,**kw):
        self.set_run_dir(self.run_dir,mode='pristine')
        g=unstructured_grid.UnstructuredGrid(max_sides=4)
        g.add_rectilinear([0,0],
                          [100,20],
                          nx=11,ny=3)
        node_z_bed=-2*np.ones(g.Nnodes())
        # node_z_bed=-2 + ((m_gate5.grid.nodes['x'][:,0] - 50) / 50).clip(0)
        g.add_node_field('node_z_bed',node_z_bed)
        super(StructureTest,self).__init__(grid=g,
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
            
        map_ds=xr.open_dataset(self.map_outputs()[0])
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
                                        cmap='jet')
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
class WithGate(StructureTest):
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
    z_right=-1.5
    Q_src_sink=0.01
    
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
                                  value=10)
        
        src_sink_return=hm.SourceSinkBC(name='sink_src',
                                        geom=np.array([ [45,10,5],
                                                        [55,10,5] ]),
                                        flow=-self.Q_src_sink)

        self.add_bcs([src_sink,src_sink_salt,src_sink_return])


class WithGateOutfall(WithGate):
    """
    Left boundary: stage, with higher salinity
    Right boundary: closed
    Gate: small-ish gate near the bed
    Outfall: slowly pull water out of the surface on the right hand side.
    """
    GateLowerEdgeLevel=-1.95
    CrestLevel=-2.0
    Q_sink=-0.01
    
    def desc(self):
        return f"Gate+sink: Q={self.Q_sink}"

    def __init__(self,**kw):
        super(WithGateOutfall,self).__init__(**kw)

    def set_bcs(self):
        left=hm.StageBC(geom=np.array([[0,0],[0,20]]),
                        name='left',
                        water_level=0.0)
        left_salt=hm.ScalarBC(parent=left,scalar='salinity',value=20)
        
        sink=hm.SourceSinkBC(name='sink',
                             geom=np.array([95,8,2.0]),
                             flow=self.Q_sink)

        self.add_bcs([left,left_salt,sink])
        
#  m_base=StructureTest(fig_num=1).go()
#  
#  m_gate=WithGate(fig_num=2).go()
#  
#  # sill_width seems to do nothing, at least when opening_width is specified
#  m_gate2=WithGate(sill_width=0.2,fig_num=3).go()
#  
#  # opening_width does make a difference, even in this case where the gate
#  # spans a single computational edge.
#  m_gate3=WithGate(opening_width=7.0,fig_num=4).go()
#  
#  # Trying to understand how A relates to geometry
#  # is the issue that opening_width should be 0?
#  m_gate4=WithGate(opening_width=0.0,sill_level=-0.7,fig_num=5).go()

#  => A=4.00.  I think that means the full edge length, 20m, and 0.2m opening
#     in the vertical.
# is the length from the edge, or from the polyline?

##
m_outfall=WithGateOutfall(Q_sink=-0.01,CrestWidth=20.0).go()

for t in range(50):
    m_outfall.summary_plot(time=t)
    plt.draw()
    plt.pause(0.01)

##
m_outfall_high=WithGateOutfall(Q_sink=-0.01,CrestWidth=20.0,
                               CrestLevel=-0.2,GateLowerEdgeLevel=-0.15,
                               fig_num=3).go()

for t in range(50):
    m_outfall_high.summary_plot(time=t)
    plt.draw()
    plt.pause(0.01)


## 
# This one looks mostly okay
m_gate_bed=WithGate( GateLowerEdgeLevel=-1.98,CrestLevel=-2.0,fig_num=6,
                     CrestWidth=0.1).go()

## 
for t in range(50):
    m_gate_bed.summary_plot(time=t)
    plt.draw()
    plt.pause(0.01)

##


# Putting the gate opening higher up doesn't have the intended effect.
# The flow decreases, but the salt is still showing up near the bed
# on the downstream side.

# Overall, it seems that the vertical distribution of salinity on the
# downstream side just reflects stability, regardless of the elevation
# of the gate opening. The elevation has some effect on the flow rate,
# with a low opening allowing more flow than a high opening.
m_gate_mid=WithGate( GateLowerEdgeLevel=-1.98,CrestLevel=-2.,fig_num=5).go()

for t in range(50):
    m_gate_mid.summary_plot(time=t)
    plt.draw()
    plt.pause(0.01)


## 
# This one looks decent
m_src=WithSrcSink(Q_src_sink=0.1,fig_num=7,right='closed').go()

for t in range(50):
    m_src.summary_plot(time=t)
    plt.draw()
    plt.pause(0.01)

m_src.summary_plot(time=10)
    
##

# It doesn't appear that the gate selectively blocks
# layers.
# It also appears that the boundary very quickly affects
# salt on the left side.
# the gate slows down the flow for sure, but there is no
# indication that the dense water from the left is only
# reaching the lower layers on the right.

# Would a pump or source/sink pair fix things?
#  try a source/sink, and a thin-dam in the middle.

# A source/sink pair does mix the fluids
# Is it mixing at a reasonable rate?
# The rhs volume is 2m D x 20m W * 50m L
# 2000 m3
# flow of a 0.01 m3/s, for 24h.
# rhs appears to go from 15 to 18ppt.
# with mostly 25 ppt coming in
# so close enough. That's a flow of 864, or 43%
# of the rhs volume. And we get abut 40% of the
# way to 25ppt.

# The vertical mixing still seems extreme

# Have to remember to turn on density effects via Idensform=2
# With that in place, the two-source-sink system looks pretty
# good.

# Turns out that having multiple edges in the structure makes
# a big difference. With two edges, widthcenter=0 will shut off
# flow. with one edge, widthcenter=0.0 does not shut off
# flow. 
    
## 
# sill_width=1.0           => A=2.1
# flow_through_height=0.2

# sill_width=2.0 = A=2.2


# Test the above in 3D.
# Does it properly route the right density through?


# In history output:
# flow_though_height: distance from sill_level==crest_level, as in a weir,
# up to gate_lower_edge_level=lower_edge_level as in sluice gate.

# Areas don't really make sense.
#  flow through height is 0.1
#  opening width 0.5
#  but somehow area is 2.2?
# 44.78x larger than expected.
# the edge length is 10.

# Guide to structures:
#   For gates:
#     opening_width is about horizontally sliding gates, and gives
#     the opening as the gates slide apart.  For a sluice or weir
#     configuration, there is no horizontal sliding, and opening_width
#     should be 0.
#     With opening_width=0.0, the water will flow between the sill_level
#     (aka crest, the lower bounding elevation), and the lower_edge_level
#     (bottom of the gate, upper bounding elevation of the flow)
#     The lateral dimension is the full length of the edges involved.
#     Even if the polyline is 2m long, if it falls on an edge 20m long,
#     the flow will take up the full 20m.
#     To constrict the lateral dimension of the flow, probably need to
#     go to generic structures.

# sill_width: if absent, uses the full edge length, 20m.
# if present, somehow only affects half of the opening?
#   Just go with generalstructure.  We'll need that eventually.
# keywords are listed in m_strucs

# Okay - so the deal is just that the area isn't reliable, whether
# it comes from history general_structure_flow_area, or from the
# transect.
# But as the height of the opening goes to 0, flow does go to zero.


## 
m_gate5.run_simulation()
m_gate5.summary_plot()

# And coeffs?
#  With A=1.0, dz=0.05, w=20, u=0.475
# extraresistance=1 => u=0.532 (?)
# drowngateflowcoeffs = 0.1 ==> u=0.0401

##
ds=xr.open_dataset(m_gate4.his_output())

for v in ds.data_vars:
    if not v.startswith('general_structure'): continue
    print(f"{v}: {ds.isel(time=-1)[v]}")
    print()

# see packages/dflowfm_kernel/src/unstruc_boundaries.f90

# there are a ton of settings, and they get defaults depending
# on specific type.
# gate: must have sill_level
#   - can be automated via REALTIME or tim file or something
# sill_width: defaults to length of crossed flow lengths.
# door_height: vertical size of the door
# lower_edge_level: elevation of lower extent of door
#   - can be automated
# opening_width==door_opening_width, can be automated

# Really have to specify everything for generalstructure
# otherwise get corrupt results.

# Something still fucked.
# A still acts like only half the edge is blocked.
#
#  [structure]
#  type         = generalstructure
#  id           = gate
#  polylinefile = gate.pli
#  GateHeight = 2
#  GateLowerEdgeLevel = -0.4
#  GateOpeningWidth = 0.0
#  CrestLevel = -0.6
#  CrestWidth=5.0
#  pos_freegateflowcoeff=1.0
#  pos_drowngateflowcoeff=1.0
#  pos_freeweirflowcoeff=1.0
#  pos_drownweirflowcoeff=1.0
#  pos_contrcoeffreegate=1.0
#  neg_freegateflowcoeff=1.0
#  neg_drowngateflowcoeff=1.0
#  neg_freeweirflowcoeff=1.0
#  neg_drownweirflowcoeff=1.0
#  neg_contrcoeffreegate=1.0
#  Upstream1Width=2
#  Upstream1Level=-20
#  Upstream2Width=1
#  Upstream2Level=-20
#  Downstream1Width=1
#  Downstream1Level=-20
#  Downstream2Width=2
#  Downstream2Level=-20
#  extraresistance=0
#  dynstructext=1
#  gateheightintervalcntrl=10000

# With all the widths set to 0.5, there is no flow,
# and some disturbance to the upstream water surface
# With downstream widths can go as small as 0.8 and its
# okay, but below that it goes unstable

# Is it any different with the most recent pre-compiled
# version (2021.02) ?
# unpacking...
# no difference

# Tracking down what's up in the source:
# unstruc_boundaries.f90:2629:
#     hulp(5, n) = huge(1d0)  ! widthcenter=10
# These get copied in togeneral to here:
# manholes.f90:1233:
#    generalstruc(ng)%widthcenter             = hulp( 5)

# Seems that a bunch of code in manholes.f90 uses widthcenteronlink(.)
# rather than just widthcenter.
# flgtarfm() is something

# widthcenteronlink is set near end of togeneral, set to to width(1:ngen)
# widths() is passed in.

# k: an index into some list of edges for all structures
# presumably L is the global edge index.
# what is Lf? what is wu?
# togeneral is called at line 2957
# appears wu is set by call at line 2256.  No, that just allocates stuff
# see delft3dfm-68124/src/utils_gpl/flow1d/packages/flow1d_core/src/structures.f90
# 


#       widthtot = 0d0
#       do k = L1cgensg(n), L2cgensg(n)
#          L  = kegen(k)
#          Lf = kcgen(3,k)
#          widths(k-L1cgensg(n)+1) = wu(Lf)
#          widthtot = widthtot + wu(Lf)
#       enddo
#       numgen = L2cgensg(n)-L1cgensg(n)+1
# 
#       ! widths(1:numgen) is what actually gets used
#       call togeneral(n, hulp(:,n), numgen, widths(1:numgen))

#
# Seems like there's no proper way to do the crest width.
# But I can get the area correct by knowing the edge length,
# set the crest width to the edge length, and adjusting
# gate lower edge level and CrestLevel.

# Negative CrestWidth does something.
# CrestWidth=20 => A=1.0 (dz=0.05)
# CrestWidth=-10 => A=0.25
# CrestWidth=-19 => A=0.025
# It's like the total area is 0.5*(edge*dz) + 0.5*CW*dz
# = 0.5*(edge+CW)*dz
# edge=edge length=20
# dz=0.05 in this case.
# Weird. But it kind of works out.

# So the next things is to move to layers.
# Set up some strat. on the left, mixed on right.
# Will a gate at a specific elevation properly convey
# only a specific density through?
# If yes, what about a gate spanning multiple layers?

# Hmm - right off the bat, looks like the layers just
# squeeze through.
# What if run with z-layers?

# Could also look into manholes.

# There is gate example that actually describes the gate in the .ext
# file, not a structures.ini file.
# Actually it has 4 channels.
# dam.pli: crosses the 2nd on at x=158m. 
# gate.pli: same as dam.pli

# general.pli: crosses 3rd and 4th
#  -- width is given here as 10
#     history output doesn't have any valid data for width just as before
#      

# leftlev.pli: BC on left

# weir1_tdk.pliz: crosses the 1st one at 210.

# as is, the ending velocity 0.142 m/s downstream (right) of the general
# structure
# changing width down to 2.0, I get 0.011 m/s downstream.
# general_structure_flow_area is entirely missing
# setting width to 0 does cut off the flow entirely.
# still no valid area information

# Limit to just the 4th channel.
# Weird. Now I get flow, even though the widthcenter is still 0.

# Does my gate example work better when there are multiple edges?
# Yes.
