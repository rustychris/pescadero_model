import pesca_base
import numpy as np
from shapely import wkt
import os
import stompy.model.schism.schism_model as sch
import stompy.model.hydro_model as hm
from stompy import utils
import six
six.moves.reload_module(pesca_base)
six.moves.reload_module(sch)

class PescaSchism(pesca_base.PescaButanoMixin,sch.SchismModel):
    salinity=False
    temperature=False

    def set_friction(self):
        # SCHISM takes friction at nodes
        # For the moment just set a constant global Cd
        # Started with 0.003, but was not frictional enough (or mouth was too open)
        self.grid.add_node_field('drag', 0.010*np.ones(self.grid.Nnodes()))
        
    def configure_global(self):
        # No horizontal viscosity or diffusion
        # self.mdu['physics','Vicouv']=0.0
        # self.mdu['physics','Dicouv']=0.0

        # self.mdu['output','MapInterval']=12*3600 # 12h.
        # self.mdu['output','RstInterval']=4*86400 # 4days
        # self.mdu['output','HisInterval']=900 # 15 minutes

        # self.mdu['physics','UnifFrictCoef']=0.023 # just standard value.

        if self.nlayers_3d>1:
            self.param['CORE','ibc']=0  # enable baroclinic
        else:
            self.param['CORE','ibc']=1  # disable baroclinic
            
        self.param['CORE','ibtp']=1 # enable scalar transport
        if self.nlayers_3d<=2:
            dt=20 # 2D runs stable and fast with dt=20
        else:
            dt=4 # 3D runs stable up to dt=4.
        self.param['CORE','dt']=dt # probably okay for barotropic run. 4s for baroclinic
        self.param['CORE','nspool']=int(3600/dt) # hourly for now
        self.param['SCHOUT','nspool_sta']=int(6*60/dt) # 6 minutes
        self.param['OPT','itr_met']=3 # TVD2, for space and time
        self.param['OPT','h_tvd']=0 # Use tvd everywhere, even in shallow areas

    def config_layers(self):
        # SCHISM is more level-focused, so I think there are always
        # at least two, representing the bottom and top of the
        # water column
        # For Pescadero, basically limited to sigma or local sigma.
        # self.config_layers_sigma()
        self.config_layers_local_sigma()
        
    def config_layers_local_sigma(self):
        n_level=max(2,self.nlayers_3d)

        sigmas=np.linspace(-1,0,n_level)
        sigma_str="\n".join(["%3d %.5f"%(1+i,sigma) for i,sigma in enumerate(sigmas)])
        
        vgrid_lines=["1 !ivcor",
                     f"{n_level} !nvrt"]
        eta_nom=2.5
        depth_nom=eta_nom - self.grid.nodes['node_z_bed']
        dz=depth_nom.max()/(n_level-1)
        n_levels=(1+depth_nom/dz).astype(np.int32).clip(2,n_level)
        bed_index=n_level-n_levels+1
        
        for i in range(self.grid.Nnodes()):
            # Each line is node index from 1, bottom level index, and sigma coordinates from -1 to 0
            sig=np.linspace(-1,0,n_levels[i])
            sigmas=" ".join(["%.3f"%s for s in sig])
            line=f"{i+1} {bed_index[i]} {sigmas}"
            vgrid_lines.append(line)
        self.vgrid_in="\n".join(vgrid_lines)
        self.monitor_z=np.linspace(0,2.0,11)
        
    def config_layers_sigma(self):
        n_level=max(2,self.nlayers_3d)

        sigmas=np.linspace(-1,0,n_level)
        sigma_str="\n".join(["%3d %.5f"%(1+i,sigma) for i,sigma in enumerate(sigmas)])
        
        self.vgrid_in=f"""2 !ivcor
{n_level} 1 1.e6 !nvrt, kz (# of Z-levels); h_s (transition depth between S and Z)
Z levels
1  -1.e6
S levels
40. 1. 1.e-4  !h_c, theta_b, theta_f
{sigma_str}
"""
        self.monitor_z=np.linspace(0,2.0,21)
        
    def write_forcing(self):
        # Force a dredge depth on all open boundaries
        for bc in self.bcs:
            if isinstance(bc,hm.StageBC) or isinstance(bc,hm.FlowBC):
                if bc.dredge_depth is None:
                    bc.dredge_depth=-1.0
                    self.log.info("Overriding dredge depth to %.3f"%bc.dredge_depth)
        super(PescaSchism,self).write_forcing()
              
    def write_extra_files(self):
        # Simulation config steps that don't have a natural/general
        # home.
        
        # Also create bed_frac, SED_hvar initial conditions.
        g=self.grid
        g.write_gr3(os.path.join(self.run_dir,'bed_frac_1.ic'),z=1.0) # one sediment class, 100%
        g.write_gr3(os.path.join(self.run_dir,'SED_hvar_1.ic'),z=0.0) # no bed sediments in IC

        g.write_gr3(os.path.join(self.run_dir,'salt.ic'),z=0.0) # fresh
        g.write_gr3(os.path.join(self.run_dir,'temp.ic'),z=20.0) # 20degC
        g.write_gr3(os.path.join(self.run_dir,'bedthick.ic'),z=0.0) # bare rock
        # sets imnp per node. Can probably set to 0.0?
        g.write_gr3(os.path.join(self.run_dir,'imorphogrid.gr3'),z=1.0)

        # only dips below 1e-6 very near boundaries. seems there is something internal
        # forcing it up to 1e-6 in most of the flow.
        g.write_gr3(os.path.join(self.run_dir,'diffmin.gr3'),z=1e-8)
        # When diffmax ==1e-7, output showed diff=0.0 everywhere
        g.write_gr3(os.path.join(self.run_dir,'diffmax.gr3'),z=1.0)

        with open(os.path.join(self.run_dir,'vgrid.in'),'wt') as fp:
            fp.write(self.vgrid_in)

        # Enable tvd everywhere (right?)
        with open(os.path.join(self.run_dir,'tvd.prop'),'wt') as fp:
            for c in range(g.Ncells()):
                fp.write("%d 1\n"%(c+1))

        self.write_inlet_morpho()

    # This forms a bank-to-bank line near the mouth
    # These are 0-based
    # morph_elts=np.array(list(range(10556,10570+1))+[61378,61379,61377,61376])

    morph_wkt="""Polygon ((552076.7757061361335218 4124658.43376859556883574, 552077.55741135939024389 4124662.18595366738736629,
552092.0971285121049732 4124667.6578902299515903, 552127.74288669310044497 4124687.51320290099829435, 552134.30921056855004281 4124642.33064099634066224, 552070.67840539466124028 4124606.99756490439176559, 552076.7757061361335218 4124658.43376859556883574))"""
    
    def write_inlet_morpho(self):
        apply_to_nodes=True # patched schism -- applies dumping as dz at nodes when index is negative
        
        ds=self.prep_qcm_data()

        # Too lazy to push this into shapefile
        morph_poly=wkt.loads(self.morph_wkt)

        # Update dumping every 15 min
        dump_dt_s=900
        sim_seconds=(self.run_stop-self.run_start)/np.timedelta64(1,'s')
        # start at t=0 but we won't output dumping at t=0
        dump_t=np.arange(0,sim_seconds+dump_dt_s,dump_dt_s)

        # target elevation
        z_thalweg=np.interp( utils.to_unix(self.run_start)+dump_t,
                             utils.to_unix(ds.time.values),ds['z_thalweg'].values)

        if apply_to_nodes:
            self.morph_nodes=self.grid.select_nodes_intersecting(morph_poly,as_type='indices')
            #nodes=np.unique( np.concatenate([self.grid.cell_to_nodes(c) for c in elts]))
            nodes=self.morph_nodes
            area=np.ones(len(nodes)) # direct elevation, so no area adjustment
            elts1=-(nodes+1) # negate and to 1-based
            z_bed=self.grid.nodes['node_z_bed'][nodes]
        else:
            self.morph_elts=self.grid.select_cells_intersecting(morph_poly,as_type='indices') 
            elts=self.morph_elts
            area=self.grid.cells_area()[elts]
            # A little tricky to figure out ground elevation -- bathy is at nodes.
            # take average to estimate element bathy
            z_cells=self.grid.interp_node_to_cell(self.grid.nodes['node_z_bed'])
            z_bed=z_cells[elts]
            elts1=1+elts # 1-based
            
        # For now, the same z_target for all elements
        z_target=np.zeros( (len(dump_t),len(elts1)), np.float64)
        z_target[:,:]=np.maximum( z_thalweg[:,None], # broadcast the same target over all elements
                                  z_bed[None,:] ) # broadcast bathy over all time
        z_target=np.round_(z_target, 3) # Don't care about sub-mm variation. just makes the files bigger.

        z_target[0,:]=z_bed # initial condition

        dz_target=np.diff(z_target,axis=0)

        with open(os.path.join(self.run_dir,'sed_dump.in'),'wt') as fp:
            fp.write("from QCM, update elevation every %s s\n"%dump_dt_s)
            # Possible bug in sediment.F90 when the simulation starts on or before
            # the time of the first dump record.
            # Here skip first dump_t, which is the initial condition, such that
            # the dumping at time t reflects dz calculated over the preceding time
            # step of dump_dt_s
            for ti,t in enumerate(dump_t[1:]):
                dzs=dz_target[ti,:]
                active=(dzs!=0.0)
                if not np.any(active):
                    continue
                active_elts1=elts1[active]
                fp.write('%g %d\n'%(t,len(active_elts1))) # t_dump, ne_dump
                dVs=(dzs*area)[active]

                for elt1,dV in zip(active_elts1,dVs):
                    # read(18,*)(ie_dump(l),vol_dump(l),l=1,ne_dump)
                    # to 1-based
                    fp.write('%d %.4f\n'%(elt1,dV))

