"""
SCHISM version
Runs targeting the 2016/2017 period of the BML field data.
Here focused on 2D runs and how various mouth treatments alter
the stage results.
"""
import matplotlib

import matplotlib.pyplot as plt
import peschism
import os
import shutil
import numpy as np
from stompy.model import hydro_model
#from stompy.model.delft import dflow_model
import pesca_base
import stompy.model.schism.schism_model as sch
import peschism as pesch

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
six.moves.reload_module(sch)
six.moves.reload_module(pesca_base)
six.moves.reload_module(pesch)


##
class PescaMouthy(pesch.PescaSchism):
    def add_mouth_structure(self):
        # Baseline:
        # super(PescaMouthy,self).add_mouth_structure()
        pass


model=PescaMouthy(run_start=np.datetime64("2016-06-09 00:00"),
                  run_stop=np.datetime64("2016-06-20 00:00"),
                  #run_start=np.datetime64("2016-12-10 00:00"),
                  #run_stop=np.datetime64("2016-12-20 00:00"),
                  #run_start=np.datetime64("2019-02-10 00:00"),
                  #run_stop=np.datetime64("2019-02-20 00:00"),
                  run_dir="data_schmouth_v032",
                  salinity=True,
                  temperature=True,
                  nlayers_3d=40)

model.param['SCHOUT','iof_hydro(21)']=1 # eddy diffusivity

model.param['OPT','mid']="'KE'" # temporary hack for string formatting
model.param['OPT','xlsc0']=0.001  # mixing length at boundaries
model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

# v020: ran, not too bad, but sed_dump was missing header line, no morph
# v021: fix header line...
# v022: patch schism to allow negative element=>elevation adjustment at node.
# v023: finer output time, finer morph update.
# v024: much longer mouth, and bump up friction to 0.01
# v025: try 3d with salt and temp
# v026: finer resolution in station output
# v027: attempt LSC2. Runs, no improvement in strat.
# v028: output eddy diffusivity, and enable TVD2 for all depths
# v029: try K-epsilon
# v030: diffmax=1e-7, xlsc0 down to 1mm.
# v031: partial revert diffmax to 1e-5, and bump up layers to 40.
# v032: kick off 80 layers, just in case it becomes a useful point of comparison
#   not any different than 40.
# revert layers to 40, undo the harsh constraints on diff.



