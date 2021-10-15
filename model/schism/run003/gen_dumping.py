from stompy.grid import unstructured_grid

g=unstructured_grid.UnstructuredGrid.read_gr3('hgrid.gr3')

##
# Have an entry every 5 minutes
T=np.arange(0,6*3600,300)

t_start=3600

# This forms a bank-to-bank line near the mouth
elts=list(range(10556,10570+1))+[61378,61379,61377,61376]

# At the end of 6 h I want 1m of deposition
dz=1.0/(T>=t_start).sum()


with open('sed_dump.in','wt') as fp:
    # Possible bug in sediment.F90 when the simulation starts on or before
    # the time of the first dump record.
    for t in T:
        if t<t_start:
            continue
        fp.write('%g %d\n'%(t,len(elts))) # t_dump, ne_dump
        volumes=dz*g.cells_area()[elts]
        
        for i,elt in enumerate(elts):
            # read(18,*)(ie_dump(l),vol_dump(l),l=1,ne_dump)
            fp.write('%d %.4f\n'%(elt,volumes[i]))
        

