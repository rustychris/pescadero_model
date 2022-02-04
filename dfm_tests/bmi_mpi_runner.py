# Simple model runs to test feasibility of BMI, esp. with MPI

# It's ugly, but can be made to work.
# updating discharge via BMI does not work. There does not appear to be a way to
# get around the built-in forcing. Easy enough to read out the forcing, but
# the BMI access to the time stepping is before the built-in forcing is calculated,
# and it appears to always overwrite my settings.
# However -- it does appear to work to extend .tim files on the fly.  So at each
# time step I can write discharge to the tim file for the next time step.
# Whether this will lead to issues when running with MPI across nodes or on a network
# filesystem, I don't know.

# MPI runs locally. Will need to update check_bmi to generate the MPI domain,
# and have it run a version of bmi_runner where rank 0 updates the forcing.
# Might be tricky since the water level data will be spread out.

# Dealing with water level data:
#  call to initialize()
#   checks whether MPI is initialized, and initializes it if not (recording whether
#   mpi was initialized by DFM or not)
#     gets rank and size, using 'DFM_COMM_DFMWORLD
#  So what is DFM_COMM_DFMWORLD?
#  in partition.F90, it is NAMECLASH_MPI_COMM_WORLD = mpi MPI_COMM_WORLD
# So in theory we can use MPI here, too. And duplicate the MPI communicator
# to keep communication here separate from DFM.
# Becomes challenging because pretty sure mpi4py has to be compiled against the 'correct'
# mpi library. For 2022.02 I think that means intel, maybe even against the exact same
# binary. With intel, that's probably doable, since already have oneapi installed.
# For running on farm, this is going to get bad I think.

# So start with the filesystem approach.


from stompy import utils
import os
import numpy as np
from stompy import utils
import bmi.wrapper
from numpy.ctypeslib import ndpointer  # nd arrays
from ctypes import (
    # Types
    c_double, c_int, c_char_p, c_bool, c_char, c_float, c_void_p,
    # Complex types
    # ARRAY, Structure,
    # Making strings
    # Pointering
    POINTER, byref, # CFUNCTYPE,
    # Loading
    # cdll
)

##

print("bmi_mpi_runner environment")
# There is a lot in here.
# could use 'MPI_LOCALRANKID' or 'PMI_RANK' as a guess on MPI rank, or use proper mpi4py
#print(os.environ)

sim=bmi.wrapper.BMIWrapper(engine="/opt/delft3dfm_2022.02/lnx64/lib-safe/libdflowfm.so")

# Just need to keep ahead of the model a little bit.
dt=300.0

rank=int(os.environ['PMI_RANK'])

print(f"[{rank}]")

if rank==0:
    t_pad=dt/60. # In minutes
    Qfp=open('runs/bmi00/src_sink.tim','wt')
    Q=np.array([0.00,0.05,0.0])
    Qfp.write("%.4f %.4f %.4f\n"%(Q[0],Q[1],Q[2]))
    Q[0]+=t_pad
    Qfp.write("%.4f %.4f %.4f\n"%(Q[0],Q[1],Q[2]))
    Qfp.flush()

print(f"[{rank}] about to initialize")
# dfm will figure out the per-rank file
sim.initialize('runs/bmi00/flowfm.mdu')

##

# simulate half a day:

while sim.get_current_time()<sim.get_end_time():
    # print(f"[{rank}] taking a step")
    
    # Write
    if rank==0:
        t_new=(dt+sim.get_current_time()) / 60.0
        Q[0]=t_new+t_pad
        Q[1]=0.05*np.cos(2*np.pi*t_new/(24*60))
        Qfp.write("%.4f %.4f %.4f\n"%(Q[0],Q[1],Q[2]))
        Qfp.flush()
        
    sim.update(dt)
        
sim.finalize()

# WORKS!
