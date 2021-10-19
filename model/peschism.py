import pesca_base
import numpy as np
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
    # def __init__(self,*a,**k):
    #     super(PescaSchism,self).__init__(*a,**k)
    #     
    #     self.set_grid_and_features()
    #     self.set_bcs()
    #     self.add_monitoring()
    #     self.add_structures()
    #     self.set_friction()

    def set_friction(self):
        # SCHISM takes friction at nodes
        # For the moment just set a constant global Cd
        self.grid.add_node_field('drag', 0.003*np.ones(self.grid.Nnodes()))
        
    def configure_global(self):
        # No horizontal viscosity or diffusion
        # self.mdu['physics','Vicouv']=0.0
        # self.mdu['physics','Dicouv']=0.0

        # self.mdu['output','MapInterval']=12*3600 # 12h.
        # self.mdu['output','RstInterval']=4*86400 # 4days
        # self.mdu['output','HisInterval']=900 # 15 minutes

        # self.mdu['physics','UnifFrictCoef']=0.023 # just standard value.

        # For starters stick to no transport -- focus on tidal cal
        self.param['CORE','ibc']=1  # disable baroclinic
        self.param['CORE','ibtp']=1 # enable scalar transport
        self.param['CORE','dt']=20 # probably okay for barotropic run. 4s for baroclinic

    def config_layers(self):
        self.param['CORE','ibc']=1  # disable baroclinic

        self.vgrid_in="""2 !ivcor
2 1 1.e6 !nvrt, kz (# of Z-levels); h_s (transition depth between S and Z)
Z levels
1  -1.e6
S levels
40. 1. 1.e-4  !h_c, theta_b, theta_f
   1    -1.
   2    0.
"""
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

        g.write_gr3(os.path.join(self.run_dir,'diffmin.gr3'),z=1e-8)
        g.write_gr3(os.path.join(self.run_dir,'diffmax.gr3'),z=1e-4)

        with open(os.path.join(self.run_dir,'vgrid.in'),'wt') as fp:
            fp.write(self.vgrid_in)

        # Enable tvd everywhere (right?)
        with open(os.path.join(self.run_dir,'tvd.prop'),'wt') as fp:
            for c in range(g.Ncells()):
                fp.write("%d 1\n"%(c+1))

        self.write_inlet_morpho()

    # This forms a bank-to-bank line near the mouth
    # These are 0-based
    morph_elts=np.array(list(range(10556,10570+1))+[61378,61379,61377,61376])
    def write_inlet_morpho(self):
        ds=self.prep_qcm_data()

        elts=self.morph_elts

        # Update dumping every 0.5h
        dump_dt_s=1800
        sim_seconds=(self.run_stop-self.run_start)/np.timedelta64(1,'s')
        # start at t=0 but we won't output dumping at t=0
        dump_t=np.arange(0,sim_seconds+dump_dt_s,dump_dt_s)

        # target elevation of the cells
        z_thalweg=np.interp( utils.to_unix(self.run_start)+dump_t,
                             utils.to_unix(ds.time.values),ds['z_thalweg'])
        # For now, the same z_target for all elements
        z_target=np.zeros( (len(dump_t),len(elts)), np.float64)
        
        # A little tricky to figure out ground elevation -- bathy is at nodes.
        # take average to estimate element bathy
        z_cells=self.grid.interp_node_to_cell(self.grid.nodes['node_z_bed'])
        z_bed=z_cells[elts]

        z_target[:,:]=np.maximum( z_thalweg[:,None], # broadcast the same target over all elements
                                  z_bed[None,:] ) # broadcast bathy over all time
        z_target[0,:]=z_bed # initial condition

        dz_target=np.diff(z_target,axis=0)

        area=self.grid.cells_area()[elts]

        with open(os.path.join(self.run_dir,'sed_dump.in'),'wt') as fp:
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
                active_elts=elts[active]
                fp.write('%g %d\n'%(t,len(active_elts))) # t_dump, ne_dump
                dVs=(dzs*area)[active]

                for elt,dV in zip(active_elts,dVs):
                    # read(18,*)(ie_dump(l),vol_dump(l),l=1,ne_dump)
                    # to 1-based
                    fp.write('%d %.4f\n'%(elt+1,dV))

