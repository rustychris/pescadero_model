# Convert pescadero grid to gr3, verify it loads in visit plugin
from stompy.grid import unstructured_grid
import os
import xarray as xr

## 
base="."
g=unstructured_grid.UnstructuredGrid.read_gr3(os.path.join(base,'hgrid.gr3'))

ds=xr.open_dataset(os.path.join(base,'outputs','schout_0000_1.nc'))

g.write_to_xarray(ds,
                  face_dimension='nSCHISM_hgrid_face',
                  node_dimension='nSCHISM_hgrid_node',
                  edge_dimension='nSCHISM_hgrid_edge')
ds.to_netcdf(os.path.join(base,'outputs','schout_0000_1_ugrid.nc'))

##

# But what if it's MPI?
base="run001"

g=unstructured_grid.UnstructuredGrid.read_gr3(os.path.join(base,'hgrid.gr3'))

## 
nprocs=max_procs=32
nseq=max_seq=100

for proc in range(max_procs):
    for seq in range(max_seq):
        nc_fn=os.path.join(base,'outputs','schout_%04d_%d.nc'%(proc,seq+1))
        if not os.path.exists(nc_fn):
            if seq==0:
                nprocs=proc
            else:
                nseq=seq
            break
        ds=xr.open_dataset(nc_fn)
        
        break
    break

##
class Local2Global(object):
    # The mapping is still confusing.
    # Based on local_to_global files, there are shared nodes
    # and shared edges, but no shared cells/elements.
    # All local cells have their requisite nodes.
    # Some local edges do not have their requisite nodes
    # Some local cells do not have their requisite edges
    def __init__(self,fn,ds=None):
        fp=open(fn,'rt')
        sizes=[int(s) for s in fp.readline().strip().split()]
        comment=fp.readline()

        Ncell=int(fp.readline().strip())
        if ds:
            assert Ncell==ds.dims['nSCHISM_hgrid_face']
        # read Ncell,2 integers
        self.cell_map=np.loadtxt(fp,np.int32,max_rows=Ncell) - 1
        Nnode=int(fp.readline().strip())
        if ds:
            assert Nnode==ds.dims['nSCHISM_hgrid_node']
        self.node_map=np.loadtxt(fp,np.int32,max_rows=Nnode) - 1
        Nedge=int(fp.readline().strip())
        if ds:
            assert Nedge==ds.dims['nSCHISM_hgrid_edge']
        self.edge_map=np.loadtxt(fp,np.int32,max_rows=Nedge) - 1

        
## 
# global_to_local.prop
#   maps elements 1..71832 to processor 0..3
def rev(ab):
    ba=np.zeros((ab[:,1].max()+1,2),np.int32)-1
    ba[ab[:,1],0] = ab[:,1]
    ba[ab[:,1],1] = ab[:,0]
    return ba
    
l2g=Local2Global(os.path.join(os.path.dirname(nc_fn),'local_to_global_%04d'%proc))

g_local=g.copy()
assert np.all(np.diff(l2g.node_map[:,0])==1)
g_local.nodes=g_local.nodes[l2g.node_map[:,1]]

assert np.all(np.diff(l2g.edge_map[:,0])==1)
# Local edges are a subset of global edges, given by l2g.edge_map
g_local.edges=g_local.edges[l2g.edge_map[:,1]]
# Edges bring along node references, at this point these are global
global_nodes=g_local.edges['nodes'].copy()
# global nodes are mapped back to local by reversing local_to_global
local_nodes=rev(l2g.node_map)[global_nodes,1]
g_local.edges['nodes']=local_nodes # has some invalid edges

# but 52 of the global nodes don't properly map to a local node
# (50 unique)
# These appear to be one halo farther into the adjacent proc
# than expected.
# unmapped_nodes=global_nodes[ local_nodes<0 ]
bad_edges=np.nonzero(np.any(local_nodes<0,axis=1))[0]
global_bad_edges=l2g.edge_map[bad_edges]

assert np.all(np.diff(l2g.cell_map[:,0])==1)
g_local.cells=g_local.cells[l2g.cell_map[:,1]]
cell_node_global=g_local.cells['nodes']
cell_node_local =np.where(cell_node_global>=0,
                          rev(l2g.node_map)[cell_node_global,1],
                          -1)
# This comes up empty. So all local cells have their respective local nodes
bad_cells=np.nonzero( np.any( (cell_node_local<0) & (cell_node_global>=0),axis=1) )[0]
g_local.cells['nodes']=cell_node_local

cell_edge_global=g_local.cells['edges']
cell_edge_local =np.where( cell_edge_global<0,
                           cell_edge_global,
                           rev(l2g.edge_map)[cell_edge_global,1])

# 54 missing. So some local cells do not have their respective local edge
bad_cells_from_edge=np.nonzero( np.any( (cell_edge_local<0) & (cell_edge_global>=0), axis=1) )[0]
g_local.cells['edges']=cell_edge_local
global_bad_cells=l2g.cell_map[bad_cells_from_edge]

g_local.refresh_metadata() # clear _node_to_edges, _node_to_cells
g_local.edges['cells']=g_local.UNKNOWN

##

# Delete missing (but don't renumber)
for c in bad_cells:
    g_local.delete_cell(c)
for j in bad_edges:
    g_local.delete_edge(j)

## 

plt.figure(1).clf()
g_local.plot_cells(color='orange',alpha=0.4,zorder=0)
g_local.plot_edges(zorder=1)
g_local.plot_nodes(color='tab:red',zorder=2)
plt.axis('tight')
plt.axis('equal')
plt.axis('off')

## 

# How hard is to have multi_ugrid handle this?
from stompy.grid import multi_ugrid
import glob

class MultiSchism(multi_ugrid.MultiUgrid):
    def __init__(self,grid_fn,paths,xr_kwargs={}):
        if not isinstance(grid_fn,unstructured_grid.UnstructuredGrid):
            self.grid=unstructured_grid.UnstructuredGrid.read_gr3(grid_fn)
        else:
            self.grid=grid_fn
            
        if isinstance(paths,str):
            paths=glob.glob(paths)
            # more likely to get datasets in order of processor rank
            # with a sort.
            paths.sort()
        self.paths=paths
        self.dss=self.load(**xr_kwargs)
        self.n_ranks=len(self.dss)
        
        # avoid loading grids -- in SCHISM the subdomain grids are
        # not as cleanly independent, but we have explicit mappings

        self.rev_meta={ 'nSCHISM_hgrid_node':'node_dimension',
                        'nSCHISM_hgrid_edge':'edge_dimension',
                        'nSCHISM_hgrid_face':'face_dimension', }

        self.create_global_grid_and_mapping()
        
    def create_global_grid_and_mapping(self):
        self.node_l2g=[] # per rank, 
        self.edge_l2g=[]
        self.cell_l2g=[]

        for rank in range(self.n_ranks):
            ds=self.dss[rank]
            nc_fn=self.paths[rank]
            
            fn=os.path.join(os.path.dirname(nc_fn),'local_to_global_%04d'%rank)
            fp=open(fn,'rt')
            sizes=[int(s) for s in fp.readline().strip().split()]
            comment=fp.readline()
            Ncell=int(fp.readline().strip())
            assert Ncell==ds.dims['nSCHISM_hgrid_face']
            c_map=np.loadtxt(fp,np.int32,max_rows=Ncell) - 1
            Nnode=int(fp.readline().strip())
            assert Nnode==ds.dims['nSCHISM_hgrid_node']
            n_map=np.loadtxt(fp,np.int32,max_rows=Nnode) - 1
            Nedge=int(fp.readline().strip())
            assert Nedge==ds.dims['nSCHISM_hgrid_edge']
            j_map=np.loadtxt(fp,np.int32,max_rows=Nedge) - 1

            # From the source file, these all include the local index.
            # verified that those are sequential, so with no further
            # munging we're done:
            self.node_l2g.append(n_map[:,1])
            self.edge_l2g.append(j_map[:,1])
            self.cell_l2g.append(c_map[:,1])
        
## 
base="run002"
ms=MultiSchism(grid_fn=os.path.join(base,'hgrid.gr3'),
               paths=os.path.join(base,'outputs','*_1.nc'))

##

elev=ms['elev'].isel(time=-1).values
##
plt.figure(1).clf()
ms.grid.contourf_node_values(elev,np.linspace(0,3,20),cmap='jet')
plt.axis('equal')

# F'ing amazing.
 
##
