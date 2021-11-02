# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:23:31 2021

@author: smunger

Run trying different mouth structures


"""
import os
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid
import subprocess
from shapely import geometry


class PescaDye(pesca_base.PescaButano):
    extraresistance=8.0
    dwaq=True

    def __init__(self,*a,**kw):
        super(PescaDye,self).__init__(*a,**kw)
        self.setup_tracers()
        self.mdu['output','MapInterval']=900

        self.mdu['output','Wrimap_velocity_component_u0']=0 #      = 1                   # Write velocity component for previous time step to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_velocity_component_u1']=0 #      = 1                   # Write velocity component to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_velocity_vector']=0 #            = 1                   # Write cell-center velocity vectors to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_upward_velocity_component']=0 #  = 1                   # Write upward velocity component on cell interfaces (1: yes, 0: no)
        self.mdu['output','Wrimap_density_rho']=0 #                = 1                   # Write flow density to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_horizontal_viscosity_viu']=0 #   = 1                   # Write horizontal viscosity to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_horizontal_diffusivity_diu']=0 # = 1                   # Write horizontal diffusivity to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_flow_flux_q1']=0 #               = 1                   # Write flow flux to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_spiral_flow']=0 #                = 1                   # Write spiral flow to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_numlimdt']=0 #                   = 1                   # Write the number times a cell was Courant limiting to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_chezy']=0 #                      = 1                   # Write the chezy roughness to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_turbulence']=0 #                 = 1                   # Write vicww, k and eps to map file (1: yes, 0: no)
        self.mdu['output','Wrimap_wind']=0 #                       = 1                   # Write wind velocities to map file (1: yes, 0: no)
    
    def add_structures(self):
        self.add_mouth_structure1()
        self.add_mouth_structure2()
        
    def add_mouth_structure1(self):
        """
        Set up flow control structure for the inner mouth structure
        """
        ds = self.prep_qcm_data()
        crest= ds['z_thalweg']
        width= ds['w_inlet']    
        
        self.add_Structure(
            type='generalstructure',
            name='mouth',
            
            Upstream2Width=100,                 	# Width left side of structure (m)
            Upstream1Width=100,                 	# Width structure left side (m)
            CrestWidth=100,                 	# Width structure centre (m)
            Downstream1Width=100,                 	# Width structure right side (m)
            Downstream2Width=100,                 	# Width right side of structure (m)
            Upstream2Level=0,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0,                   	# Bed level right side structure (m AD)
            Downstream2Level=0,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=0,                  	# Gate lower edge level (m AD)
            pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
            pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
            pos_freeweirflowcoeff=1,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=1,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                  	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=1,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=1,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=self.extraresistance,                   	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            )
    def add_mouth_structure2(self):
        """
        Set up flow control structure for the inner mouth structure
        """
        ds = self.prep_qcm_data()
        crest= ds['z_thalweg']
        width= ds['w_inlet']    
        
        self.add_Structure(
            type='generalstructure',
            name='mouth_B',
            
            Upstream2Width=100,                 	# Width left side of structure (m)
            Upstream1Width=100,                 	# Width structure left side (m)
            CrestWidth=100,                 	# Width structure centre (m)
            Downstream1Width=100,                 	# Width structure right side (m)
            Downstream2Width=100,                 	# Width right side of structure (m)
            Upstream2Level=0,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0,                   	# Bed level right side structure (m AD)
            Downstream2Level=0,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=0,                  	# Gate lower edge level (m AD)
            pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
            pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
            pos_freeweirflowcoeff=1,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=1,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                  	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=1,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=1,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=self.extraresistance,                   	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            )

    # Configure age tracers
    def setup_tracers(self):
        """                                                                                                                                                                                                                                  Set up Delwaq model to run with Dflow. Currently used to calculate age of water using nitrification process                                                                                                                          """
        # For starters, have a single flushing-time tracer, flushed by tides or creeks.
        self.dwaq.substances['NO3']=self.dwaq.Sub(initial=0.0)   # age-concentration
        # self.dwaq.substances['RcNit']=self.dwaq.Sub(initial=0.0) #
        self.dwaq.parameters['RcNit']=1.0 # age accumulates everywhere.
        self.dwaq.parameters['NH4']=1     # age accumulates everywhere.
        
        #self.dwaq.substances['RcNit']=self.dwaq.Sub(initial=0.0) # when tracking true age, this is the concentration tracer.

        # Will need to let it run for a day, stop, update the scalar values, and restart.
        self.dwaq.substances['marsh']=self.dwaq.Sub(initial=0.0)
        self.dwaq.substances['pond']=self.dwaq.Sub(initial=1.0)
        
        #self.dwaq.substances['nonsac']=self.dwaq.Sub(initial=0.0) # Tag for non-Sac returns
        #self.dwaq.substances['sea']=self.dwaq.Sub(initial=0.0) # Tag for water coming from seaward BCs

        # enable age kludge
        self.dwaq.parameters['TcNit']=1  # no temp. dependence
        self.dwaq.add_process(name='Nitrif_NH4')  # by default, nitrification process uses pragmatic kinetics forumulation (SWVnNit = 0)

    def run_simulation(self):
        try:
            print(self.run_dir)
            if self.num_procs<=1:
                nthreads=8
            else:
                nthreads=1
            super(PescaDye,self).run_simulation(threads=nthreads)
        except subprocess.CalledProcessError as exc:
            print(exc.output.decode())
            raise

    def set_grid_and_features(self):
        super(PescaDye,self).set_grid_and_features()
        # After the fact switch to Sophie's grid
        import local_config
        grid_dir=os.path.join(local_config.model_dir,"../grids/pesca_butano_v03")
        self.set_grid(os.path.join(grid_dir, f"pesca_butano_{self.terrain}_deep_bathy_mod3.nc"))
        

## This set up for tidal conditions July 2016 (16 days), use extraresistance=8
# model=PescaDye(run_start=np.datetime64("2016-07-09 00:00"),
#                               run_stop=np.datetime64("2016-07-25 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p07",
#                               salinity=False,
#                               temperature=False,
#                               extraresistance=8)

# # This set up for tidal condition July 2017 (31 days), use extraresistance=8
# model=PescaDye(run_start=np.datetime64("2017-07-15 00:00"),
#                     run_stop=np.datetime64("2017-08-15 00:00"),
#                     run_dir="run_dye_test-p08",
#                     salinity=False,
#                     temperature=False,
#                     extraresistance=8)

# if 1:
#     # Adjust for getting inundation maps
#     # 1 month of 12h output was 620M
#     # half the duration
#     # bump the frequency by factor of 24
#     # that's at 6GB?
#     # There are 14 time-varying map outputs
#     # Can disable most of those, really just care about water level,
#     # maybe bed stress.
#     # Should get us under 1GB.
#     model.run_stop=np.datetime64("2017-07-31 00:00")

# v10a,b: worked, though still fairly porous
# v11a,b: a few more levee features
# v12a,b: use Sophie's grid. A bit better, but not great.
#         Matches high water with both v11 and QCM, low water not nearly
#         as low as QCM, though. What little observations there are look
#         entirely different than QCM.
# v13a,b: back to 2016-12-10 breach
run_dir_a="run_dye_test-v13a"
run_dir_b="run_dye_test-v13b"

if PescaDye.run_completed(run_dir_a):
    print("Looks like first phase, %s, has completed"%run_dir_a)
else:
    # This set up for breaching condition December 2016 (19 days), use extraresistance=1
    model=PescaDye(run_start=np.datetime64("2016-12-10 00:00"),
                   run_stop=np.datetime64("2016-12-10 06:00"),
                   #run_start=np.datetime64("2016-03-06 00:00"),
                   #run_stop=np.datetime64("2016-03-06 01:00"),        
                   run_dir=run_dir_a,
                   salinity=False,
                   temperature=False,
                   extraresistance=1)
    model.write()
    model.partition()
    model.run_simulation()

model0=PescaDye.load(run_dir_a)
model=PescaDye(restart_from=model0, run_stop=np.datetime64("2016-12-17 00:00"),
               run_dir=run_dir_b,
               # restart logic is not smart enough to copy these over
               # and load does not populate them in model0
               salinity=False,
               temperature=False,
               extraresistance=1)

# Update initial condition to set tracer distributions

geom_marsh=model.get_geometry(desc='marsh',type='dye')
geom_pond =model.get_geometry(desc='pond',type='dye')

def modify_ic(ds,**kw):
    # ds['marsh'] and ds['pond'] are set, dims of time, nFlowElem
    elem_xy=np.c_[ds['FlowElem_xzw'].values,ds['FlowElem_yzw'].values]

    is_marsh=[1.0 if geom_marsh.intersects(geometry.Point(xy)) else 0.0 for xy in elem_xy]
    is_pond= [1.0 if geom_pond.intersects(geometry.Point(xy)) else 0.0 for xy in elem_xy]
    ds['marsh'].values[:]=is_marsh
    ds['pond'].values[:]=is_pond

    return ds

model.modify_restart_data(modify_ic)

# Restart files appear correct, but the output is really crazy.
# 1.0 becomes 4.125e6, 0 becomes -999
# The pond is correctly marked, but marsh is scattered in chunks

print("Configured restart from ",model.run_start)
model.write()
model.partition() # copies pre-partitioned data over
model.run_simulation()
