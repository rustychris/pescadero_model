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

# NEXT: try MPI run locally. Will need to update check_bmi to generate the MPI domain,
# and have it run a version of bmi_runner where rank 0 updates the forcing.
# Might be tricky since the water level data will be spread out.




# Some weirdness where it appears to fail sometimes, not sure what is changing
# to affect that. might have been errors in the mdu/ext.

# Second issue is that it does not retain my discharge setting.
# HERE: try changing FlowFM.ext to have a constant discharge.

# Checking on temmerman example
#  during the simulation 'rnveg' is what gets updated.
#  that's plant density. In bmi_get_var.inc, there is a distinction
#  between
#    rnveg, 3D plant density , 2D part is basis input (1/m2) {"location": "face", "shape": ["ndkx"]},
#  and
#  stemdens, TEMP 2D plant density (1/m2) {"location": "face", "shape": ["ndx"]}

# QUANTITY=stemdensity
# FILENAME=stdens.xyz
# FILETYPE=7
# METHOD=6
# OPERAND=O

from stompy import utils
import numpy as np

# seems I need to import stuff to get ctypes to be happy?
## 

# Now try things with BMI:
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

sim=bmi.wrapper.BMIWrapper(engine="/opt/delft3dfm_2022.02/lnx64/lib-safe/libdflowfm.so")

# Just need to keep ahead of the model a little bit.
t_pad=300/60.
Qfp=open('runs/bmi00-mod/src_sink.tim','wt')
Q=np.array([0.00,0.05,0.0])
Qfp.write("%.4f %.4f %.4f\n"%(Q[0],Q[1],Q[2]))
Q[0]+=t_pad
Qfp.write("%.4f %.4f %.4f\n"%(Q[0],Q[1],Q[2]))
Qfp.flush()

sim.initialize('runs/bmi00-mod/flowfm.mdu')

@utils.add_to(sim)
def get_scalar_double(self,name):
    """
    Read a scalar double. DFM seems not to handle some of the type/shape/rank
    queries, so here we force it.
    Return value is a numpy scalar -- for updating, modify this and pass back
    to set_var
    """ 
    c_name = bmi.wrapper.create_string_buffer(name)
    get_var = self.library.get_var
    rank=0
    shape=()
    arraytype = ndpointer(dtype="double",
                          ndim=rank,
                          shape=shape,
                          flags='F')

    get_var.argtypes = [c_char_p, POINTER(arraytype)]
    get_var.restype = None
    data = arraytype()
    # Get the array
    get_var(c_name, byref(data))
    if not data:
        print("NULL pointer returned")
        return None
    elif hasattr(data, 'contents'):
        array = data.contents
        # for numpy <= 1.14
    else:
        array = np.ctypeslib.as_array(data)

    return array

##
# sim.get_time_step() # DtUser = 300s
# This had worked, but now I'm getting "NULL pointer access."
# Did I lose something in translation?
# Not sure. continues to fail.
dt=300.0

# This change doesn't seem to hold.
# Qsrc_sink=sim.get_scalar_double('sourcesinks/src_sink/discharge')
# Qsrc_sink[()]=0.1 # easiest to just overwrite the returned value and pass it back
# sim.set_var('sourcesinks/src_sink/discharge',Qsrc_sink)
# Qsrc_sink=sim.get_scalar_double('sourcesinks/src_sink/discharge')
# print("Qsrc_sink post set:",Qsrc_sink)

##

#Qsink_src=sim.get_scalar_double('sourcesinks/sink_src/discharge')
#Qsink_src[()]=0.0 # easiest to just overwrite the returned value and pass it back
#sim.set_var('sourcesinks/sink_src/discharge',Qsink_src)

##
# simulate half a day:

while sim.get_current_time()<sim.get_end_time():
    # Write
    t_new=(dt+sim.get_current_time()) / 60.0
    Q[0]=t_new+t_pad
    Q[1]=0.05*np.cos(2*np.pi*t_new/(24*60))
    Qfp.write("%.4f %.4f %.4f\n"%(Q[0],Q[1],Q[2]))
    Qfp.flush()

    Qsrc_sink=sim.get_scalar_double('sourcesinks/src_sink/discharge')
    print("Qsrc_sink before update: ",Qsrc_sink)
    sim.update(dt)
    Qsrc_sink=sim.get_scalar_double('sourcesinks/src_sink/discharge')
    print("Qsrc_sink at the end of run:",Qsrc_sink)

sim.finalize()

##
# even with constant values in the ext, I still don't seem to get my values to
# stay put.

# No luck in removing or truncating time series data.
# No luck in seting operator=A
# No luck with operator=A, and setting Q after taking one timestep.



# bmi.update
# unstruc.F90: subroutine flow_run_sometimesteps(dtrange, iresult)
#           call flow_init_usertimestep(iresult)
#           call flow_single_timestep(key, iresult)
#           call flow_finalize_usertimestep(iresult)
# 
# unstruc.F90: subroutine flow_init_usertimestep(iresult)
#    !> Initializes a new user-timestep (advances user time, sets new meteo forcing)
#       call flow_setexternalforcings(tim1fld ,.false. , iresult)    ! set field oriented forcings. boundary oriented forcings are in
# 
# unstruc.F90: subroutine flow_setexternalforcings(tim, l_initPhase, iresult)
# 
# 
# lots of stuff in here
#  pumps with levels
#  valves
#  ...
#  success = success .and. ec_gettimespacevalue(ecInstancePtr, item_discharge_salinity_temperature_sorsin, irefdate, tzone, tunit, tim)
# 
# meteo1.f90:
#    interface ec_gettimespacevalue
#       module procedure ec_gettimespacevalue_by_itemID
#       module procedure ec_gettimespacevalue_by_name
#    end interface ec_gettimespacevalue
#  
# utils_lgpl/ec_module/packages/ec_module/src/ec_module.f90:630:   function ec_gettimespacevalue_by_itemID
# 
# ecGetValues(instancePtr, itemId, ecReqTime, target_array)
# ec_item.f90: recursive function ecItemGetValues(instancePtr, itemId, timesteps, target_array) result(success)
#   success = ecItemUpdateTargetItem(instancePtr, itemPtr, timesteps)
# 




