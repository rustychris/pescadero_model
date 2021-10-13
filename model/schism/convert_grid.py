# Convert pescadero grid to gr3, verify it loads in visit plugin
from stompy.grid import unstructured_grid
from stompy.plot import plot_utils
import six
six.moves.reload_module(unstructured_grid)

## 

def prep_grid(g):
    g.edges['mark']=g.INTERNAL
    g.add_edge_field('bc_id',-np.ones(g.Nedges(),np.int32),on_exists='overwrite')


def mark_open(g,linestring):
    # Mark open boundaries, then come back and infer land
    j_open=g.select_edges_by_polyline(linestring)
    g.edges['mark'][j_open]=g.OPEN
    g.edges['bc_id'][j_open]=0

def mark_land(g):
    e2c=g.edge_to_cells()

    # each string starts/ends with the same node
    strings=g.boundary_linestrings(return_nodes=True,sort=True)

    #  Need to walk through the strings, skip over edges that
    #  are already marked open. check whether first/last strings
    #  can be combined.
    #  Add each string as a land boundary.
    land_bc_count=0
    for si,string in enumerate(strings):
        land_strings=[] # this string, broken up into land boundaries
        land_string=[] # string under construction
        for a,b in zip(string[:-1],string[1:]):
            j=g.nodes_to_edge([a,b])
            # Is this edge already part of a bc?
            if g.edges['mark'][j]==0: # nope
                land_string.append([a,j,b])
            else:
                # hit an edge that is already BC
                if land_string:
                    land_strings.append(land_string)
                    land_string=[]
        if land_string:
            land_strings.append(land_string)
        # Check for joining first and last:
        if len(land_strings)>1 and land_strings[0][0][0]==land_strings[-1][-1][2]:
            land_strings[0]=land_strings[-1] + land_strings.pop(-1)
        # And if there is only one, break it into two (I think some part of schism
        # can't handle a single continuous boundary)
        L=len(land_strings)
        if L==1:
            ls=land_strings[0]
            land_strings=[ ls[:L//2],ls[L//2:] ]
        # And write marks back to grid
        for land_string in land_strings:
            for a,j,b in land_string:
                g.edges['mark'][j]=unstructured_grid.SchismGrid.BC_LAND
                g.edges['bc_id'][j]  =land_bc_count
            land_bc_count+=1

##
# Fabricate some edge markers:
g=unstructured_grid.UnstructuredGrid.read_ugrid("../../grids/pesca_butano_v03/pesca_butano_existing_deep_bathy_mod3.nc")

if 0:
    bc=plot_utils.draw_polyline()
else:
    bc=np.array([[ 552085.03859468, 4124876.22985261],
                 [ 552028.61833959, 4124795.52746242],
                 [ 551996.48021961, 4124741.96392911],
                 [ 551958.62865607, 4124673.40260648]])
prep_grid(g)
mark_open(g,bc)
mark_land(g)

g.write_gr3(os.path.basename(g.filename).replace('.nc','.gr3'))

