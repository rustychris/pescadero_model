# How hard is to have multi_ugrid handle this?

from stompy.grid import multi_ugrid, unstructured_grid
import matplotlib.pyplot as plt
import glob
import numpy as np
import os
import stompy.plot.cmap as scmap
from stompy import utils

turbo=scmap.load_gradient('turbo.cpt')
## 
import six
six.moves.reload_module(multi_ugrid)

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
base="run005"
g=unstructured_grid.UnstructuredGrid.read_gr3(os.path.join(base,'hgrid.gr3'))
##

ms=MultiSchism(grid_fn=g,
               paths=os.path.join(base,'outputs','*_2.nc'))
ms.reload()

##

# Try to show the vertical grid along the transect
from stompy.spatial import wkb2shp, linestring_utils
from stompy import utils

feats=wkb2shp.shp2geom("../../grids/pesca_butano_v03/line_features.shp")
# [N,{x,y}] points from ocean to PC3
thalweg=np.array(feats[ feats['name']=='thalweg_pesc' ][0]['geom'])
#thalweg=linestring_utils.resample_linearring(thalweg,5,closed_ring=0)

## Get a node string that follow thalweg
nodes=g.select_edges_by_polyline(thalweg,return_nodes=True,boundary=False)

## 
# plt.figure(1).clf()
# g.plot_edges(color='0.6',lw=0.3)
# plt.plot( g.nodes['x'][nodes,0],
#           g.nodes['x'][nodes,1],color='orange',lw=1.0)


dist=utils.dist_along(g.nodes['x'][nodes])
plt.figure(2).clf()

for ti in range(0,72,6):
    ax.plot(dist,-g.nodes['depth'][nodes],color='k',label='bed')
    eta=ms.elev.isel(nSCHISM_hgrid_node=nodes,time=ti).values
    ax.plot(dist,eta,color='b',label='eta')

    for ni,n in enumerate(nodes):
        zcors=ms.zcor.isel(time=ti,nSCHISM_hgrid_node=n).values
        ax.plot(dist[ni]*np.ones_like(zcors),zcors,'g.')

    # Can I plot a salt transect?
    tran_salt=ms.salt.isel(time=ti,nSCHISM_hgrid_node=nodes)
    tran_z   =ms.zcor.isel(time=ti,nSCHISM_hgrid_node=nodes)

    tran=xr.Dataset()
    tran['x_sample']=('sample',),g.nodes['x'][nodes,0]
    tran['y_sample']=('sample',),g.nodes['x'][nodes,1]
    tran['d_sample']=('sample',),dist
    tran['z_int']=('sample','layer'),tran_z.data
    tran['salt']=('sample','layer'),tran_salt.data
    x,y=xr.broadcast(tran.d_sample, tran.z_int)
    coll=ax.pcolor(x,y,tran.salt,cmap='jet')
    plt.colorbar(coll)
    fig.canvas.draw()
    plt.pause(0.01)

##
# # Understanding vertical coordinates and wetdry
# plt.figure(1).clf()
# fig,ax=plt.subplots(num=1)
# g.plot_nodes( values=ms.wetdry_node.isel(time=0).values, cmap='coolwarm')
# 
# # Only a narrow swath is dry at output step=0
# wet=np.nonzero(0==ms.wetdry_node.isel(time=0).values)[0]
# 
# msn=ms.isel(nSCHISM_hgrid_node=wet[0])
# msn.hvel.isel(time=-1,two=0)
# # => array([1.2710776e-05, 1.2710776e-05], dtype=float32)
# # So this wet node has two layers, both have valid output, with identical values.
# 
# msn.zcor.isel(time=-1)
# # <xarray.DataArray 'zcor' (nSCHISM_vgrid_layers: 2)>
# # array([0.276677  , 0.90733975], dtype=float32)
# 
# # depth of this node in the grid is -0.276677


for t in range(0,ms.dims['time'],12):
    val=ms['elev'].isel(time=t).values
    V=np.linspace(0.3,1.5,30)
    #val=utils.mag(ms['dahv'].isel(time=t).values)
    #V=np.linspace(0.0,1.5,30)

    plt.figure(1).clf()
    fig,ax=plt.subplots(num=1)
    cset=ms.grid.contourf_node_values(val,V,cmap=turbo,extend='both',
                                      ax=ax)
    plt.colorbar(cset)
    ax.axis('equal')
    ax.axis( (551895.5684811207, 552433.8489916292, 4124386.230383094, 4124906.422821157))
    ax.text(0.1,0.1,str(t), transform=ax.transAxes)
    fig.canvas.draw()
    plt.pause(0.05)
##

for t in range(0,ms.dims['time']):
    #val=ms['elev'].isel(time=t).values
    #V=np.linspace(0.3,1.5,30)
    
    #val=utils.mag(ms['dahv'].isel(time=t).values)
    #V=np.linspace(0.0,1.5,30)

    val=ms['salt'].isel(time=t,nSCHISM_vgrid_layers=1).values
    V=np.linspace(0.3,30,60)

    plt.figure(1).clf()
    fig,ax=plt.subplots(num=1)
    cset=ms.grid.contourf_node_values(val,V,cmap=turbo,extend='both',
                                      ax=ax)

    # overlay dry elements in gray
    ms.grid.plot_cells(mask=ms['wetdry_elem'].isel(time=t).values==1,color='0.7',zorder=1)
                       
    plt.colorbar(cset)
    ax.axis('equal')
    ax.axis( (551895.5684811207, 552433.8489916292, 4124386.230383094, 4124906.422821157))
    ax.text(0.1,0.1,str(t), transform=ax.transAxes)
    fig.canvas.draw()
    plt.pause(0.01)

##

for i in range(1,29):
    ms=MultiSchism(grid_fn=g,
                   paths=os.path.join(base,'outputs','*_%i.nc'%i))
    #ms.reload()
    for t in range(0,ms.dims['time'],72):
        #val=ms['elev'].isel(time=t).values
        #V=np.linspace(0.3,1.5,30)

        #val=utils.mag(ms['dahv'].isel(time=t).values)
        #V=np.linspace(0.0,1.5,30)

        val=ms['salt'].isel(time=t,nSCHISM_vgrid_layers=1).values
        V=np.linspace(0.3,30,60)

        fig=plt.figure(1)
        fig.clf()
        ax=fig.add_axes([0,0,1,1])

        cset=ms.grid.contourf_node_values(val,V,cmap=turbo,extend='both',
                                          ax=ax)

        # overlay dry elements in gray
        ms.grid.plot_cells(mask=ms['wetdry_elem'].isel(time=t).values==1,color='0.7',zorder=1)

        plt.colorbar(cset)
        ax.axis('equal')
        # ax.axis( (551895.5684811207, 552433.8489916292, 4124386.230383094, 4124906.422821157))
        ax.axis( (551827.9587318085, 553362.964047032, 4123960.06985914, 4124904.4578948733) )
        ax.text(0.1,0.1,str(t), transform=ax.transAxes)
        fig.canvas.draw()
        plt.pause(0.01)
##

import stompy.model.schism.schism_model as sch

model=sch.SchismModel.load('schism/run003')

ms=model.map_output(1)
##

plt.figure(1).clf()
fig,ax=plt.subplots(num=1)

ms.grid.plot_edges(color='k',lw=0.3)

#ms.grid.contourf_node_values(ms['elev'].isel(time=35).values,
#                             np.linspace(0.4,1.5,50),cmap=turbo)

ms.grid.contourf_node_values(ms['zcor'].isel(time=35,nSCHISM_vgrid_layers=0).values,
                             np.linspace(0.0,1.5,50),cmap=turbo)

ax.axis( (552018.8933133289, 552232.6829957409, 4124518.199465297, 4124757.140875052))
