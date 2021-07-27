# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:23:31 2021

@author: smunger

Run trying different mouth structures


---> probably need to restart Kernel everytime for it to work otherwise I get a cdip_mop..... error
"""
import os
import pesca_base_1ms
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid
import subprocess

class PescaChgMouth(pesca_base_1ms.PescaButano):
    def add_mouth_structure(self):
        """
        Set up flow control structure for the inner mouth structure
        """
        ds = self.prep_qcm_data()

        crest= ds['z_thalweg']
        width= ds['w_inlet']    
        
        self.add_Structure(
            type='generalstructure',
            name='mouth',
            
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
            GateLowerEdgeLevel=0.2,                  	# Gate lower edge level (m AD)
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
            extraresistance=10,                   	# Extra resistance (-)
            GateHeight=10,                   	# Vertical gate door height (m)
            GateOpeningWidth=width,                 	# Horizontal opening width between the doors (m)
            #GateOpeningHorizontalDirection=symmetric,           	# Horizontal direction of the opening doors
            )

model=PescaChgMouth(run_start=np.datetime64("2016-07-12 12:00"),
                              run_stop=np.datetime64("2016-07-16 12:00"),
                              run_dir="E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v46",
                              salinity=False,
                              temperature=False)

# np.datetime64("2016-11-03 00:00"),
#                               run_stop=np.datetime64("2016-11-05 00:00")

# model=pesca_base.PescaButano(run_start=np.datetime64("2016-07-12 12:00"),
#                              run_stop=np.datetime64("2016-07-26 12:00"),
#                              run_dir="E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v17C",
#                              salinity=False,
#                              temperature=False)

#assert not os.path.exists(model.run_dir), 'Directory already exist'

model.mdu
model.write()
#model.partition()

try:
    model.run_simulation(threads=8)
except subprocess.CalledProcessError as exc:
    print(exc.output.decode())
    raise





'''
run_tide_test-v46  --> use 1 mouth structure
2016-07-12 12:00 -2016-07-16 12:00
grid:v03 -- pesca_butano_v03_existing_deep_bathy.nc
mouth
pesca_base_1ms
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
pesca_base_1ms
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
pesca_base_1ms
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










