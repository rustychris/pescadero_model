# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:23:31 2021

@author: smunger

Run trying different mouth structures


---> probably need to restart Kernel everytime for it to work otherwise I get a cdip_mop..... error
"""
import os
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid
import subprocess

class PescaChgMouth(pesca_base.PescaButano):
        
    def add_structures(self):
        self.add_mouth_structure1()
        self.add_mouth_structure2()

        
    def add_mouth_structure1(self):
        """♣
        Set up flow control structure for the inner mouth structure
        """
        ds = self.prep_qcm_data()
        crest= ds['z_thalweg']
        width= ds['w_inlet']    
        
        self.add_Structure(
            type='generalstructure',
            name='mouth',
            
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=0,                  	# Gate lower edge level (m AD)
            pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
            pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
            pos_freeweirflowcoeff=1,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=1,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                   	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=1,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=1,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=1,                   	# Extra resistance (-)
            GateHeight=6,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            #GateOpeningHorizontalDirection=symmetric,           	# Horizontal direction of the opening doors
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
            
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
            GateLowerEdgeLevel=0,                  	# Gate lower edge level (m AD)
            pos_freegateflowcoeff=1,                   	# Positive free gate flow (-)
            pos_drowngateflowcoeff=1,                   	# Positive drowned gate flow (-)
            pos_freeweirflowcoeff=1,                   	# Positive free weir flow (-)
            pos_drownweirflowcoeff=1,                   	# Positive drowned weir flow (-)
            pos_contrcoeffreegate=1,                   	# Positive flow contraction coefficient (-)
            neg_freegateflowcoeff=1,                   	# Negative free gate flow (-)
            neg_drowngateflowcoeff=1,                   	# Negative drowned gate flow (-)
            neg_freeweirflowcoeff=1,                   	# Negative free weir flow (-)
            neg_drownweirflowcoeff=1,                   	# Negative drowned weir flow (-)
            neg_contrcoeffreegate=1,                   	# Negative flow contraction coefficient (-)
            extraresistance=1,                   	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            #GateOpeningHorizontalDirection=symmetric,           	# Horizontal direction of the opening doors
            )


# model=PescaChgMouth(run_start=np.datetime64("2016-06-09 00:00"),
#                               run_stop=np.datetime64("2016-06-25 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p01",
#                               salinity=False,
#                               temperature=False)

# model=PescaChgMouth(run_start=np.datetime64("2016-07-09 00:00"),
#                               run_stop=np.datetime64("2016-07-25 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p02",
#                               salinity=False,
#                               temperature=False)

model=PescaChgMouth(run_start=np.datetime64("2016-12-10 00:00"),
                              run_stop=np.datetime64("2016-12-17 00:00"),
                              run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p05",
                              salinity=False,
                              temperature=False)

# model=PescaChgMouth(run_start=np.datetime64("2017-07-15 00:00"),
#                               run_stop=np.datetime64("2017-08-15 00:00"),
#                               run_dir="E:/proj/Pescadero/Model_Runs/Production/run_tide_test-p04",
#                               salinity=False,
#                               temperature=False)

        


#assert not os.path.exists(model.run_dir), 'Directory already exist'

model.mdu
model.write()
#model.partition()

try:
    print(model.run_dir)
    model.run_simulation(threads=8)    
except subprocess.CalledProcessError as exc:
    print(exc.output.decode())
    raise





'''
PRODUCTION RUN p04 -- Summer 2017 tidal

run_tide_test-p04  --> use 2 mouth structure on adjacent rows. 
2017-07-15 -2017-08-15--> Tidal
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

PRODUCTION RUN p03 -- December 2016 Close to open

run_tide_test-p03  --> use 2 mouth structure on adjacent rows. 
2016-12-01 -2016-12-17--> Tidal
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------
PRODUCTION RUN p02 -- July 2016 Tidal

run_tide_test-p02  --> use 2 mouth structure on adjacent rows. 
2016-07-09 -2016-07-25--> Tidal
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

PRODUCTION RUN p01 -- June 2016 Tidal

run_tide_test-p01  --> use 2 mouth structure on adjacent rows. 
2016-06-09 -2016-06-25--> Tidal
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v93  --> use 2 mouth structure on adjacent rows. 
2016-08-01 -2016-08-05--> 
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
Time period that filt best 2020 record

extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v92  --> use 2 mouth structure on adjacent rows. 
2016-12-10 -2016-12-15--> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
just like v88 but using friction inlet m = 0.005, side m = 0.02

extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v91  --> use 2 mouth structure on adjacent rows. 
2016-10-29 00:00 -2016-11-04 00:00 --> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
just like v80 but using friction inlet m = 0.005, side m = 0.02

extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v88  --> use 2 mouth structure on adjacent rows. 
2016-12-10 -2016-12-15--> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v81  --> use 2 mouth structure on adjacent rows. 
2016-07-12 12:00 -2016-07-19 12:00 --> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v80  --> use 2 mouth structure on adjacent rows. 
2016-10-29 00:00 -2016-11-04 00:00 --> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v76  --> use 2 mouth structure on adjacent rows. 
2016-10-29 00:00 -2016-11-04 00:00 --> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v75 --> correct the head_incr (was all uniform) to 0.5,0.3,0,0.3,0.5
crest_incr[ind] = crest[ind] + head_incr*crest[ind] 
2016-12-09 00:00 -2016-12-13 00:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=5, 


---------------------------------------------------

run_tide_test-v74  --> use 2 mouth structure on adjacent rows. 
2016-12-09 00:00 -2016-12-19 00:00 --> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v73  --> use 2 mouth structure on adjacent rows. 
2016-07-12 12:00 -2016-07-26 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v71  --> use 2 mouth structure on adjacent rows. 
2016-12-09 00:00 -2016-12-13 00:00 --> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=8, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v70  --> use 2 mouth structure on adjacent rows. 
2016-12-09 00:00 -2016-12-13 00:00 --> close to open
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v69  --> use 2 mouth structure on adjacent rows. 
2016-11-03 00:00 -2016-11-05 00:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v68  --> use 2 mouth structure on adjacent rows. 
2016-07-12 12:00 -2016-07-26 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v67 --> correct the head_incr (was all uniform) to 0.5,0.3,0,0.3,0.5
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=5, 

---------------------------------------------------

run_tide_test-v66 --> correct the head_incr (was all uniform) to 0.7,0.6,0,0.6,0.7
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=5, 

---------------------------------------------------

run_tide_test-v65  --> use 2 mouth structure on adjacent rows. 
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v64  --> use 2 mouth structure on adjacent rows. 
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v63  --> use 2 mouth structure on adjacent rows. 
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=6, 
uniform friction
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v62  --> uses 5 weirs 0.75,0.5,0,0.5,0.75
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

lat_contr_coeff=5, 

---------------------------------------------------
run_tide_test-v61  --> correct the head_incr (was all uniform) to 0.75,0.5,0,0.5,0.75
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=5, 

---------------------------------------------------
run_tide_test-v60  --> uses 5 weirs 0.75,0.5,0,0.5,0.75
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc

lat_contr_coeff=1, 

---------------------------------------------------

run_tide_test-v59  --> correct the head_incr (was all uniform) to 0.75,0.5,0,0.5,0.75
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=1, 

---------------------------------------------------

run_tide_test-v58  --> test commenting mouth parameters for multiple gates
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=5, 

---------------------------------------------------
run_tide_test-v57  --> test commenting mouth parameters for multiple gates
2016-07-12 12:00 -2016-07-14 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=2, 

---------------------------------------------------

run_tide_test-v56  --> test commenting mouth parameters for multiple gates
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
test the 5 mouths structure
extraresistance=10, 

---------------------------------------------------
run_tide_test-v55  --> test commenting mouth parameters for multiple gates
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
---------------------------------------------------

run_tide_test-v54  --> test commenting mouth parameters for multiple gates
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
---------------------------------------------------
run_tide_test-v53  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
just like 51 but using friction inlet m = 0.02, side m = 0.02 -- base case
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v52  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
just like 51 but using friction inlet m = 0.02, side m = 0.1
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v51  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
just like 43 but using friction inlet m = 0.02, side m = 0.08
            Upstream2Width=40,                 	# Width left side of structure (m)
            Upstream1Width=35,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
----------------------------------------------

run_tide_test-v50  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
extraresistance=10, 
just like 43 but using friction inlet m = 0.02, side m = 0.08
            Upstream2Width=40,                 	# Width left side of structure (m)
            Upstream1Width=35,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=1,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
----------------------------------------------
run_tide_test-v49  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth

extraresistance=10, 
just like 43 but using friction inlet m = 0.02, side m = 0.08
            Upstream2Width=60,                 	# Width left side of structure (m)
            Upstream1Width=40,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=60,                 	# Width structure right side (m)
            Downstream2Width=40,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=1,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
----------------------------------------------
run_tide_test-v48  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth

extraresistance=10, 
just like 43 but using friction inlet m = 0.02, side m = 0.08
Upstream2Width = 60
Upstream1Width = 50
CrestWidth = 50
Downstream1Width = 60
Downstream2Width = 40
Upstream2Level = 0.5
Upstream1Level = 0.5
CrestLevel = mouth_CrestLevel.tim
Downstream1Level = 0.5
Downstream2Level = 0.5
----------------------------------------------

run_tide_test-v47  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth

extraresistance=10, 
            Upstream2Width=40,                 	# Width left side of structure (m)
            Upstream1Width=35,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=40,                 	# Width structure right side (m)
            Downstream2Width=35,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=1,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=0.2,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.2,                   	# Bed level right side of structure (m AD)
----------------------------------------------


-> v44, v45, v46 are all the same. 
run_tide_test-v46  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth

extraresistance=10, 
            Upstream2Width=30,                 	# Width left side of structure (m)
            Upstream1Width=20,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=40,                 	# Width structure right side (m)
            Downstream2Width=35,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=1,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
----------------------------------------------

run_tide_test-v45  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth

extraresistance=10, 
            Upstream2Width=40,                 	# Width left side of structure (m)
            Upstream1Width=35,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=30,                 	# Width structure right side (m)
            Downstream2Width=20,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=1,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
----------------------------------------------

run_tide_test-v44  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth

extraresistance=10, 
            Upstream2Width=30,                 	# Width left side of structure (m)
            Upstream1Width=20,                 	# Width structure left side (m)
            CrestWidth=50,                 	# Width structure centre (m)
            Downstream1Width=30,                 	# Width structure right side (m)
            Downstream2Width=20,                 	# Width right side of structure (m)
            Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
            Upstream1Level=1,                   	# Bed level left side structure (m AD)
            CrestLevel=crest,	# Bed level at centre of structure (m AD)
            Downstream1Level=1,                   	# Bed level right side structure (m AD)
            Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
----------------------------------------------

run_tide_test-v43  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
pesca_base_1ms
extraresistance=10, 
Upstream2Width = 60
Upstream1Width = 40
CrestWidth = 50
Downstream1Width = 60
Downstream2Width = 40
Upstream2Level = 0.5
Upstream1Level = 0.5
CrestLevel = mouth_CrestLevel.tim
Downstream1Level = 0.5
Downstream2Level = 0.5
----------------------------------------------

run_tide_test-v42  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
pesca_base_1ms
extraresistance=8, 
----------------------------------------------

run_tide_test-v41  --> use 1 mouth structure
2016-11-03 00:00 -2016-11-05 00:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
pesca_base_1ms
extraresistance=6, 
----------------------------------------------

run_tide_test-v40  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
pesca_base_1ms
extraresistance=6, 
----------------------------------------------

run_tide_test-v39 
2016-07-12 12:00 -2016-07-23 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth_in
same para as v38 but
extraresistance=6, 
----------------------------------------------

run_tide_test-v38 
2016-07-12 12:00 -2016-07-23 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth_in
same para as v37 but
extraresistance=4, 
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=40,                 	# Width structure left side (m)
----------------------------------------------

run_tide_test-v37
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth_in
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
extraresistance=3, 

----------------------------------------------
run_tide_test-v36 --> using original grid to compare
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v01 -- pesca_butano_v01_existing_bathy.nc
mouth_in
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
extraresistance=3, 

----------------------------------------------
run_tide_test-v35
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth_in
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
extraresistance=3, 

----------------------------------------------
run_tide_test-v34
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v03 -- pesca_butano_v03_existing_bathy.nc
mouth_in
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
extraresistance=3, 

----------------------------------------------

run_tide_test-v33
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v04
mouth_in2
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
extraresistance=3, 

No change between v32 and v33
----------------------------------------------

run_tide_test-v32
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v04
mouth
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)
extraresistance=3, 

Not a lot of difference between v30/31 and v32
----------------------------------------------

run_tide_test-v31
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v04
mouth_in2
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=0.5,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0.5,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

results: no difference between v30 and v31
----------------------------------------------
run_tide_test-v30
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v04
mouth_in2
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0,                   	# Bed level left side of structure (m AD)
Upstream1Level=0,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0,                   	# Bed level right side structure (m AD)
Downstream2Level=0,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v29
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v03
mouth_in2
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0,                   	# Bed level left side of structure (m AD)
Upstream1Level=0,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0,                   	# Bed level right side structure (m AD)
Downstream2Level=0,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v28
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
grid:v01
mouth_in
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0,                   	# Bed level left side of structure (m AD)
Upstream1Level=0,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0,                   	# Bed level right side structure (m AD)
Downstream2Level=0,                   	# Bed level right side of structure (m AD)

----------------------------------------------

run_tide_test-v27
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
mouth_in
grid v03
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0,                   	# Bed level left side of structure (m AD)
Upstream1Level=0,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0,                   	# Bed level right side structure (m AD)
Downstream2Level=0,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v26
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
mouth_in
grid v02
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0,                   	# Bed level left side of structure (m AD)
Upstream1Level=0,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0,                   	# Bed level right side structure (m AD)
Downstream2Level=0,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v25
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
mouth_in
grid: v01
Upstream2Width=60,                 	# Width left side of structure (m)
Upstream1Width=55,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=60,                 	# Width structure right side (m)
Downstream2Width=55,                 	# Width right side of structure (m)
Upstream2Level=0,                   	# Bed level left side of structure (m AD)
Upstream1Level=0,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=0,                   	# Bed level right side structure (m AD)
Downstream2Level=0,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v24A
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
same as v23 just different period
Upstream2Width=40,                 	# Width left side of structure (m)
Upstream1Width=20,                 	# Width structure left side (m)
CrestWidth=50,                 	# Width structure centre (m)
Downstream1Width=40,                 	# Width structure right side (m)
Downstream2Width=20,                 	# Width right side of structure (m)
Upstream2Level=0.5,                   	# Bed level left side of structure (m AD)
Upstream1Level=1,                   	# Bed level left side structure (m AD)
CrestLevel=crest,	# Bed level at centre of structure (m AD)
Downstream1Level=1,                   	# Bed level right side structure (m AD)
Downstream2Level=0.5,                   	# Bed level right side of structure (m AD)

----------------------------------------------
run_tide_test-v24
dfm v.2021.04
2016-07-12 12:00 -2016-07-15 12:00
same as v23 just different period
----------------------------------------------

run_tide_test-v23
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Old grid v01
Use mouth_in2 for the inner mouth structure
same setting as V21 and 18_01
----------------------------------------------
run_tide_test-v22
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Old grid v01
Use mouth for the inner mouth structure
Upstream2Width=30,          	
Upstream1Width=20
Want to test how model handle width smaller than gate opening
Downstream2Level=0.5
----------------------------------------------

run_tide_test-v21
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Old grid v01
Use mouth for the outer mouth structure
mouth parameters like the old ones
correct the mistake I make where I modified the outer mouth instead of the inner mouth
in this run it's like 20B01 but mouth_in is replaced by mouth'
----------------------------------------------
run_tide_test-v20B01
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Old grid v01
Like 20 jus different time period
Use mouth for the outer mouth structure
mouth parameters like the old ones
----------------------------------------------
run_tide_test-v20B
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Like 20 jus different time period
Use mouth for the outer mouth structure
mouth parameters like the old ones
----------------------------------------------
run_tide_test-v20A
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Like 20 jus different time period
Use mouth for the outer mouth structure
mouth parameters of v19
----------------------------------------------
run_tide_test-v20
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Like 18
Use mouth for the outer mouth structure
mouth parameters of V19
----------------------------------------------
run_tide_test-v19
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Like 18
Upstream2Width=40,                 
Upstream1Width=20,  
Downstream2Level=0 
Using previous mouth parameters
----------------------------------------------
run_tide_test-v18_01
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Old grid v01
Base case to work on mouth mixing and little tide
Using previous mouth parameters

----------------------------------------------
run_tide_test-v18
dfm v.2021.04
2016-11-03 00:00 -2016-11-05 00:00
Base case to work on mouth mixing and little tide
Using previous mouth parameters
----------------------------------------------

run_tide_test-v17B
dfm v.2021.04
2016-07-12 12:00 -2016-07-23 12:00
Same as run_tide_test-v13C
Change initial water level to auto
with overtoppping and seepage in routine
change resistance back to 4
----------------------------------------------

run_tide_test-v17A
dfm v.2021.04
2016-07-12 12:00 -2016-07-23 12:00
Same as run_tide_test-v13C
Change initial water level to 1.3
change resistance to 6
----------------------------------------------
run_tide_test-v17
dfm v.2021.04
2016-07-12 12:00 -2016-07-23 12:00
Same as run_tide_test-v13C
Just to test if the new pesca_base with new grid make 
a difference
----------------------------------------------
run_tide_test-v16F
dfm v.2021.04
In DeltaShell
2016-10-25 -2016-11-09 
Use qcm interpolated z_ocean for BC, 
initial WL at 2.6

----------------------------------------------
run_tide_test-v16E
dfm v.2021.04
In DeltaShell
2016-10-31 -2016-11-01 
Use qcm interpolated z_ocean for BC, 
initial WL at 2.7
Yay it worked

----------------------------------------------

run_tide_test-v16C
dfm v.2021.04
In DeltaShell
2016-10-13 12:00 -2016-10-19 12:00
Test on close condition, set init WL at 1.5m 
Use qcm z_ocean for BC

----------------------------------------------
run_tide_test-v16B
dfm v.2021.04
In DeltaShell
2016-10-13 12:00 -2016-10-19 12:00
Test on close condition, set init WL at 1.5m 
Use qcm z_ocean for BC

----------------------------------------------
run_tide_test-v16A
dfm v.2021.04
2016-10-13 12:00 -2016-10-19 12:00
Test on close condition, set init WL at 2.10m 
see if the waterlevel rises. Mouth completely shut. 
No sources or sinks yet
----------------------------------------------
run_tide_test-v16
dfm v.2021.04
2016-08-04 12:00 -2016-08-10 12:00
Test on close condition
----------------------------------------------

run_tide_test-v15
dfm v.2021.04
2017-07-07 12:00 -2017-07-12 12:00
Validation--open
----------------------------------------------

run_tide_test-v13C
dfm v.2021.04
2016-07-12 12:00 -2016-07-23 12:00
like 13B but longer period
----------------------------------------------

run_tide_test-v13B
dfm v.2021.04
2016-07-12 12:00 -2016-07-14 12:00
extraresistance       = 4                   	# Extra resistance (-)
put all the flowcoeff = 1
['MapFormat']=4  # change the output format
2 mouth structures. 
Test to see if change to pesca_base works
----------------------------------------------

run_tide_test-v13A
dfm v.2021.04
2016-07-12 12:00 -2016-07-14 12:00
extraresistance       = 4                   	# Extra resistance (-)
put all the flowcoeff = 5
['MapFormat']=4  # change the output format
2 mouth structures. 
----------------------------------------------

run_tide_test-v13
dfm v.2021.04
2016-07-12 12:00 -2016-07-14 12:00
extraresistance       = 4                   	# Extra resistance (-)
['MapFormat']=4  # change the output format
2 mouth structures. 
----------------------------------------------


run_tide_test-v12A
dfm v.2021.04
2016-07-12 12:00 -2016-07-14 12:00
extraresistance       = 4                   	# Extra resistance (-)
['MapFormat']=4  # change the output format

----------------------------------------------

run_tide_test-v12
dfm v.2021.04
2016-07-12 -2016-07-17
extraresistance       = 3                   	# Extra resistance (-)

----------------------------------------------
run_tide_test-v11F
dfm v.2021.04
2016-07-12 -2016-07-14
extraresistance       = 3                   	# Extra resistance (-)

----------------------------------------------

run_tide_test-v11E
dfm v.2021.04
2016-07-12 -2016-07-12
extraresistance       = 1.2                   	# Extra resistance (-)

----------------------------------------------
run_tide_test-v11D
dfm v.2021.04
2016-07-12 -2016-07-12
extraresistance       = 0                   	# Extra resistance (-)
neg_drownweirflowcoeff=5,                   	# Negative drowned weir flow (-)
pos_drownweirflowcoeff=5,                   	# Positive drowned weir flow (-)

----------------------------------------------
run_tide_test-v11C
dfm v.2021.04
2016-07-12 -2016-07-12
extraresistance= 0.7                   	# Extra resistance (-)

----------------------------------------------

run_tide_test-v11B
dfm v.2021.04
2016-07-12 -2016-07-12
extraresistance       = 0                   	# Extra resistance (-)
neg_drownweirflowcoeff=1.5,                   	# Negative drowned weir flow (-)
pos_drownweirflowcoeff=1.5,                   	# Positive drowned weir flow (-)

----------------------------------------------
run_tide_test-v11A
dfm v.2021.04
2016-07-12 -2016-07-12
extraresistance       = 0.25                   	# Extra resistance (-)

----------------------------------------------
run_tide_test-v11
dfm v.2021.04
2016-07-12 -2016-07-12

type='generalstructure',
name='mouth',

Upstream2Width        = 60                 	# Width left side of structure (m)
Upstream1Width        = 55                 	# Width structure left side (m)
CrestWidth            = 50                 	# Width structure centre (m)
Downstream1Width      = 55                 	# Width structure right side (m)
Downstream2Width      = 60                 	# Width right side of structure (m)
Upstream2Level        = 1                   	# Bed level left side of structure (m AD)
Upstream1Level        = 1                   	# Bed level left side structure (m AD)
CrestLevel            = crest	# Bed level at centre of structure (m AD)
Downstream1Level      = 1                   	# Bed level right side structure (m AD)
Downstream2Level      = 1                   	# Bed level right side of structure (m AD)
GateLowerEdgeLevel    = 0.2                  	# Gate lower edge level (m AD)
pos_freegateflowcoeff = 1                   	# Positive free gate flow (-)
pos_drowngateflowcoeff= 1                   	# Positive drowned gate flow (-)
pos_freeweirflowcoeff = 1                   	# Positive free weir flow (-)
pos_drownweirflowcoeff= 1                   	# Positive drowned weir flow (-)
pos_contrcoeffreegate = 1                   	# Positive flow contraction coefficient (-)
neg_freegateflowcoeff = 1                   	# Negative free gate flow (-)
neg_drowngateflowcoeff= 1                   	# Negative drowned gate flow (-)
neg_freeweirflowcoeff = 1                   	# Negative free weir flow (-)
neg_drownweirflowcoeff= 1                   	# Negative drowned weir flow (-)
neg_contrcoeffreegate = 1                   	# Negative flow contraction coefficient (-)
extraresistance       = 0                   	# Extra resistance (-)
GateHeight            = 10                   	# Vertical gate door height (m)
GateOpeningWidth      = width                 	# Horizontal opening width between the doors (m)
GateOpeningHorizontalDirection= symmetric           	# Horizontal direction of the opening doors
)

'''










