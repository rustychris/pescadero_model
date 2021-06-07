"""
Render a large-ish grid figure highlighting the grid geometry
and how the bathymetry falls on to the grid
"""

from stompy.grid import unstructured_grid
import stompy.plot.cmap as scmap
import matplotlib.pyplot as plt

turbo=scmap.load_gradient('turbo.cpt')
##

g_exist=unstructured_grid.UnstructuredGrid.read_ugrid('pesca_butano_v02_existing_bathy.nc')
g_built=unstructured_grid.UnstructuredGrid.read_ugrid('pesca_butano_v02_asbuilt_bathy.nc')
                                                
##

for (g,name) in [ (g_exist,'Existing Conditions'),
                  (g_built,'As-Built') ]:
    fig=plt.figure(1)
    fig.clf()
    fig.set_size_inches((8,10),forward=True)

    ax=fig.add_axes([0,0,1,1])
    ax.axis('off')
    ax.axis('equal')

    g.plot_edges(color='k',lw=0.4,alpha=0.4,ax=ax)
    if 0:
        g.contourf_node_values(g.nodes['node_z_bed'],cmap=turbo)
    else:
        tri=g.mpl_triangulation()
        coll=ax.tripcolor(tri,g.nodes['node_z_bed'],cmap=turbo)
        coll.set_clim([0,4.5])
        
    cax=fig.add_axes([0.65,0.65,0.02,0.25])
    plt.colorbar(coll,label='Elevation (m NAVD88)',cax=cax)

    ax.text(0.5,0.93,f"{name}\n{g.filename}",
            transform=ax.transAxes)
    fig_fn=f"grid-{name}.pdf"
    fig.savefig(fig_fn)
    
