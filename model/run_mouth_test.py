# -*- coding: utf-8 -*-
"""
Created on Thu May  6 10:23:31 2021

@author: smunger

Run trying different mouth structures


---> probably need to restart Kernel everytime for it to work
"""
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid


class PescaChgMouth(pesca_base.PescaButano):
    def add_mouth_structure(self):
        # Override mouth parameters and pull from QCM output.
        # The mouth may require some testing...
        # For now, will try using the opening width to set width
        # rather than CrestWidth. CrestLevel sets lower edge,
        
        ds = self.prep_qcm_data()

        crest= ds['z_thalweg']-0.1
        width= ds['w_inlet'] - ds['w_inlet']*0.2      
        
        self.add_Structure(
            type='gate',
            name='mouth',
            # here the gate is never overtopped
            GateHeight=10.0, # top of door to bottom of door
            GateLowerEdgeLevel=0.2, # elevation of bottom of 'gate'
            GateOpeningWidth=width, # width of opening. 
            CrestLevel=crest, # this will be the thalweg elevation 
            #CrestWidth=  ,# should be the length of the edges
            #GateOpeningHorizontalDirection= symmetric  # Horizontal direction of the opening doors
            )


# Match up with a bit of the UCB model period
model=PescaChgMouth(run_start=np.datetime64("2016-07-12 00:00"),
                             run_stop=np.datetime64("2016-07-14 00:00"),
                             run_dir="E:/proj/Pescadero/Model_Runs/Testing/run_tide_test-v010",
                             salinity=False,
                             temperature=False,
                             
                             )



model.mdu
model.write()
model.partition()
model.run_simulation(threads=8)


'''
run_tide_test-v08
Let try if new time period work for now. 
2017-07-20 - 2017-07-20

run_tide_test-v08_2021
with the dfm v.2021.04
2017-07-20 - 2017-07-20

run_tide_test-v09
change time period
2016-07-12 -2016-07-12

run_tide_test-v10
dfm v.2021.04
2016-07-12 -2016-07-12
crest= ds['z_thalweg']-0.1
width= ds['w_inlet'] - ds['w_inlet']*0.2     


'''










