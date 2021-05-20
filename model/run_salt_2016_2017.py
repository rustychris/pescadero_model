"""
Runs targeting the 2016/2017 period of the BML field data
"""
import pesca_base
import numpy as np
from stompy.model import hydro_model
from stompy.model.delft import dflow_model
from stompy.grid import unstructured_grid

class PescaWideCulvert(pesca_base.PescaButano):
    def add_pch_structure(self):
        # originally this was a 0.4m x 0.5 m
        # opening. Try instead for a wide, short
        # opening to decease CFL issues.
        A=0.4*0.5
        z_crest=0.6 # matches bathy.
        width=8.0
        self.add_Structure(
            type='gate',
            name='pch_gate',
            GateHeight=1.5, # top of door to bottom of door
            GateLowerEdgeLevel=z_crest + A/width, # elevation of top of culvert
            GateOpeningWidth=0.0, # gate does not open
            CrestLevel=z_crest, 
            CrestWidth=width, # extra wide for decreased CFL limitation
        )

## 
model=PescaWideCulvert(run_start=np.datetime64("2016-05-20 00:00"),
                       run_stop=np.datetime64("2016-05-20 12:00"),
                       run_dir="run_salt_20160520-v53",
                       salinity=True,
                       temperature=True,
                       nlayers_3d=14,
                       num_procs=16)
# For debugging:
# 2021.01 ran well with Idensform=0
# model.mdu['physics','Idensform']=0 # 0: uniform density

# Try adjusting node elevations to avoid being just below interfaces.
z_node=model.grid.nodes['node_z_bed'] # positive up
kmx=model.nlayers_3d
z_interfaces=np.linspace(-0.25,3.25,kmx+1)
dz_bed=z_interfaces[ np.searchsorted(z_interfaces,z_node).clip(0,kmx)] - z_node
thresh=0.05
# will deepen these nodes.  Could push them up or down depending
# on which is closer, but generally we end up lacking conveyance to
# err on the side of deepening
adjust=np.where((dz_bed>0)&(dz_bed<thresh),
                thresh-dz_bed, 0)
model.grid.nodes['node_z_bed']-=adjust

model.mdu['output','MapInterval']=1800
# These don't appear to do anything
#  model.mdu['output','Wrimap_ancillary_variables']=1
#  model.mdu['output','Wrimap_volume1']=1
#  model.mdu['output','Wrimap_DTcell']=1 # include more time step limitation output

model.mdu['geometry','Layertype']=2 # z-layer
# These changes around v11-v13 did not substantially improve results.
model.mdu['numerics','CFLmax']=0.8 # more conservative
model.mdu['geometry','BedlevType']= 5 # had been 4. 6 is good for avoid scalar issues, but not for stability

# Try specifying these, but very close to the default values.
model.mdu['geometry','ZlayBot']=-0.25
model.mdu['geometry','ZlayTop']=3.25
#model.mdu['geometry','Keepzlayeringatbed']=0 # stair stepping, doesn't seem to work.
#model.mdu['geometry','Zlayercenterbedvel']=0 # avoid tricky velo reconstruction at bed? no help.
#model.mdu['numerics','Horadvtypzlayer']=1 # had been 0. 1 is default, 2 is sigma-like.
# This didn't appear to make any difference.
# model.mdu['geometry','Numtopsig']=3 # try making near surface sigma layers?

#model.mdu['geometry','StretchType']=1
# Have to be fairly precise to avoid dfm complaining about the sum
# thicknesses.
#fracs=np.diff(np.round(np.linspace(0,100,1+model.nlayers_3d),4))
#model.mdu['geometry','stretchCoef']=" ".join(["%.4f"%f for f in fracs])

model.mdu['numerics','MinTimestepBreak']=0.001
model.mdu['time','AutoTimestep']=3 # 5=bad. 4 okay but slower, seems no better than 3.
model.mdu['time','AutoTimestepNoStruct']=1 # had been 0

# Diagnosing time step slowdown
model.mdu['time','Timestepanalysis']=1

model.write()
model.partition()
model.run_simulation()

