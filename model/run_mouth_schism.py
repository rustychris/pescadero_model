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
                  run_dir="data_schmouth_v020",
                  salinity=False,
                  temperature=False,
                  nlayers_3d=0)

# model.mdu['output','MapInterval']=1800
# model.mdu['time','DtUser']=30.
# model.mdu['numerics','CFLmax']=0.4
# model.mdu['time','AutoTimestepNoStruct']=1

model.write()

shutil.copyfile(__file__,os.path.join(model.run_dir,"script.py"))
shutil.copyfile("pesca_base.py",os.path.join(model.run_dir,"pesca_base.py"))
model.partition()
model.run_simulation()

