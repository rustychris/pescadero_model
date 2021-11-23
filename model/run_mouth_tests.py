"""
Runs targeting the 2016/2017 period of the BML field data.
Here focused on 2D runs and how various mouth treatments alter
the stage results.
"""
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import pesca_base
import os
import shutil
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy import utils
from stompy.grid import unstructured_grid
import stompy.plot.cmap as scmap
turbo=scmap.load_gradient('turbo.cpt')
from stompy.plot import plot_wkb
from shapely import ops, geometry
import re

import six
six.moves.reload_module(unstructured_grid)
six.moves.reload_module(hydro_model)
six.moves.reload_module(dflow_model)
six.moves.reload_module(pesca_base)


##
class PescaMouthy(pesca_base.PescaButano):
    # Note that the salinity runs have been dropping the thalweg by 0.15 cm
    def add_mouth_structure(self):
        # Baseline:
        # super(PescaMouthy,self).add_mouth_structure()

        # synthetic DEM instead of structures
        #self.add_mouth_as_bathy()

        # synthetic DEM as structures
        # self.add_mouth_as_structures()

        # now just one mouth structure
        self.add_mouth_gen_structure(name='mouth_out')

model=PescaMouthy(#run_start=np.datetime64("2016-06-09 00:00"),
                  #run_stop=np.datetime64("2016-06-20 00:00"),
                  run_start=np.datetime64("2016-12-10 00:00"),
                  run_stop=np.datetime64("2016-12-20 00:00"),
                  run_dir="data_mouth_v035",
                  salinity=False,
                  temperature=False,
                  nlayers_3d=0,
                  pch_area=2.0)

model.mdu['output','MapInterval']=1800
model.mdu['geometry','ChangeVelocityAtStructures']=1
# model.mdu['time','DtUser']=30.
model.mdu['numerics','CFLmax']=0.5
model.mdu['numerics','Teta0']=0.7

# model.mdu['time','AutoTimestepNoStruct']=1

## 
model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

# v000:
# Getting a segfault. Happens the same for serial or mpi. Traceback mentions
# setdt, setdtorg.
# Clearing conda doesn't help.
# Occurs for 2021.03 *and* my local compile, appears to be same location.
# Related to timestepping options I had for 3D.  Moved those to config_layers(),
# Now running okay.
# Not *super* fast, though.  Maybe 1h for the whole thing?

# v001: flat synthetic bed in there...
# v002: oops, only adjusted levels for one of the mouth structures.  this remedies it
# v003: linear channel profile
# v004: change extra resistance from 4 to 1
# v005: manually add pillars.  too small, little change
# v006: big pillars. Decent improvement?
# v007: big pillars, drop the second mouth structure.
# v008: switch to bedlevel=5 to be consistent with 3D, should be comparable to 3D v114.
# v009: mimic salt run v116. is 2D still super different?
# v010: wacky structures
# v011: wacky structures, no extraresistance
# v012: wacky structures, trapezoidish
# v013: slightly narrower channel, offset down
# v014: shift the start/stop a bit later to test for spinup effects
# v015: back to v013 period, a bit longer, and use new bathy 20210820
# v016: winter breach period with mouth_as_structures. Fails during the breach 
# v017: winter breach, back to two structures with resistance (like salt v116)
#     seem to have deleted this one.
# v018: longer period like v015, but with the mouth structures.
#     appears to be identical to v015.

# v019: Flow event -- probably won't work due to missing qcm data
#    this has been shifted to run_highflow

# v020: Longer period covering neap

# v021: Return to v016-ish, mouth_as_structures, but try DFM option to omit
#       acceleration over structures.
#       Stable, but not a great improvement in draining ability.
# v022: Broader trapezoidal channel.
# v023: Taper structures in the longitudinal direction
# v024: More conservative eta and CFLmax choices
# v025: Dredge the bathy around the structures
#       very twitchy
# v026: diagnosing hydraulic controls. one structure, winter breach.
# v027:  bring in dredged mouth (via DEM)
# v028:  +-freeweircoefficients down to 0.5 (note these all have extraresistance=10)
# v029:  +-freeweircoefficients up to 2.0 (note these all have extraresistance=10)
#      might have overwritten v029 with v030.
#      freeweircoefficients back to 1.0, and extraresistance to 0.
# v030:  drop upstream/downstream levels. Not sure why they had gotten higher...
# v031:  from v030, free weir coeffs to 10
# v032:  free and drowned weir coeffs to 10.
# v033:  test mouth_as_structures with the large flow coefficients
#        not stable.
# v034:  test single structure, no extraresistance, winter breach, free/drowned coeff 0.55
#         Didn't look that great.
# v035:  same, but use mouth_out
