from stompy.grid import unstructured_grid

g=unstructured_grid.UnstructuredGrid.read_gr3('hgrid.gr3')

##
# Have an entry every 5 minutes

# I want to ramp up over 12 h, then ramp down for 12 h
T=np.arange(0,24*3600,300)

z_targets=np.array([[3600,0],
                    [12*3600,1],
                    [24*3600,0]])

# This forms a bank-to-bank line near the mouth
elts=list(range(10556,10570+1))+[61378,61379,61377,61376]

# At the end of 6 h I want 1m of deposition
z_discrete=np.interp(T,
                     z_targets[:,0],z_targets[:,1])
dz_discrete=np.r_[0,np.diff(z_discrete)]

## dz=1.0/(T>=t_start).sum()

Ac=g.cells_area()

with open('sed_dump.in','wt') as fp:
    fp.write("%g m every %g s, after t=%d\n"%(dz,T[1]-T[0],t_start))
    # Possible bug in sediment.F90 when the simulation starts on or before
    # the time of the first dump record.
    for ti,t in enumerate(T):
        if ti==0 or dz_discrete[ti]==0.0:
            continue
        fp.write('%g %d\n'%(t,len(elts))) # t_dump, ne_dump
        dz=dz_discrete[ti]
        volumes=dz*Ac[elts]
        
        for i,elt in enumerate(elts):
            # read(18,*)(ie_dump(l),vol_dump(l),l=1,ne_dump)
            fp.write('%d %.4f\n'%(elt,volumes[i]))
        
## 
# Also create bed_frac, SED_hvar initial conditions.
g.write_gr3('bed_frac_1.ic',z=1.0) # one sediment class, 100%
g.write_gr3('SED_hvar_1.ic',z=0.0) # no bed sediments in IC
g.write_gr3('salt.ic',z=0.0) # fresh
g.write_gr3('temp.ic',z=20.0) # 20degC
g.write_gr3('bedthick.ic',z=0.0) # bare rock
# sets imnp per node. Can probably set to 0.0?
g.write_gr3('imorphogrid.gr3',z=1.0)

## 
#
with open('tvd.prop','wt') as fp:
    for c in range(g.Ncells()):
        fp.write("%d 1\n"%(c+1))
