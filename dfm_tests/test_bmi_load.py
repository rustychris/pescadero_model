# Sorting out linking issues
import bmi.wrapper

# Resetting rpath on libdflowfm helps.
# Put all the non-system libraries in lib-safe.
# That all works fine.
# Turns out that libdflowfm implicitly requires libmetis.so
# so add it with patchelf --add-needed
# And this works!

sim=bmi.wrapper.BMIWrapper(engine="/opt/delft3dfm_2022.02/lnx64/lib-safe/libdflowfm.so")

# This loads everything, 
sim.initialize('runs/bmi00/flowfm.mdu')

