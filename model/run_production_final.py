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

class PescaChgMouth(pesca_base.PescaButano):
    extraresistance=8.0
    
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



## This set up for tidal conditions July 2016 (16 days), use extraresistance=8
# model=PescaChgMouth(run_start=np.datetime64("2016-07-09 00:00"),
#                               run_stop=np.datetime64("2016-07-25 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p07",
#                               salinity=False,
#                               temperature=False,
#                               extraresistance=8)

# This set up for tidal condition July 2017 (31 days), use extraresistance=8
model=PescaChgMouth(run_start=np.datetime64("2017-07-15 00:00"),
                    run_stop=np.datetime64("2017-08-15 00:00"),
                    run_dir="run_tide_test-p08",
                    salinity=False,
                    temperature=False,
                    extraresistance=8)

if 1:
    # Adjust for getting inundation maps
    # 1 month of 12h output was 620M
    # half the duration
    # bump the frequency by factor of 24
    # that's at 6GB?
    # There are 14 time-varying map outputs
    # Can disable most of those, really just care about water level,
    # maybe bed stress.
    # Should get us under 1GB.
    model.run_stop=np.datetime64("2017-07-31 00:00")
    
    model.mdu['output','MapInterval']=1800
    model.mdu['output','Wrimap_velocity_component_u0']=0 #      = 1                   # Write velocity component for previous time step to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_velocity_component_u1']=0 #      = 1                   # Write velocity component to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_velocity_vector']=0 #            = 1                   # Write cell-center velocity vectors to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_upward_velocity_component']=0 #  = 1                   # Write upward velocity component on cell interfaces (1: yes, 0: no)
    model.mdu['output','Wrimap_density_rho']=0 #                = 1                   # Write flow density to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_horizontal_viscosity_viu']=0 #   = 1                   # Write horizontal viscosity to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_horizontal_diffusivity_diu']=0 # = 1                   # Write horizontal diffusivity to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_flow_flux_q1']=0 #               = 1                   # Write flow flux to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_spiral_flow']=0 #                = 1                   # Write spiral flow to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_numlimdt']=0 #                   = 1                   # Write the number times a cell was Courant limiting to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_chezy']=0 #                      = 1                   # Write the chezy roughness to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_turbulence']=0 #                 = 1                   # Write vicww, k and eps to map file (1: yes, 0: no)
    model.mdu['output','Wrimap_wind']=0 #                       = 1                   # Write wind velocities to map file (1: yes, 0: no)
        
# # This set up for breaching condition December 2016 (19 days), use extraresistance=1
# model=PescaChgMouth(run_start=np.datetime64("2016-12-10 00:00"),
#                               run_stop=np.datetime64("2016-12-29 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p06",
#                               salinity=False,
#                               temperature=False,
#                               extraresistance=1)

    

#assert not os.path.exists(model.run_dir), 'Directory already exist'

model.mdu
model.write()
model.partition()

try:
    print(model.run_dir)
    if model.num_procs<=1:
        nthreads=8
    else:
        nthreads=1
    model.run_simulation(threads=nthreads)
except subprocess.CalledProcessError as exc:
    print(exc.output.decode())
    raise





'''

----------------------------------------------
PRODUCTION RUN P08 -- Summer 2017 tidal like P04 with different struc param for comparison

run_tide_test-p08  --> use 2 mouth structure on adjacent rows. 
2017-07-15 -2017-08-15--> Tidal
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

extraresistance=8, 
uniform friction
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

----------------------------------------------
PRODUCTION RUN P07 -- July 2016 Tidal like P02 with different struc param for comparison

run_tide_test-p07  --> use 2 mouth structure on adjacent rows. 
2016-07-09 -2016-07-25--> Tidal
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

extraresistance=8, 
uniform friction
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

----------------------------------------------


PRODUCTION RUN p06 -- December 2016 Close to open

run_tide_test-p03  --> use 2 mouth structure on adjacent rows. 
2016-12-10 -2016-12-29--> breach
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

extraresistance=1, 
uniform friction
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

'''

