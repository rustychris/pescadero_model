import os
import stompy.model.delft.dflow_model as dfm

dfm_root="/home/rustyh/src/dfm/delft3dfm_2021.03/lnx64"
lib=os.path.join( dfm_root,"lib")
if 'LD_LIBRARY_PATH' in os.environ:
    # cluster often has stuff in here already
    os.environ['LD_LIBRARY_PATH']=lib+":"+os.environ['LD_LIBRARY_PATH']
else:
    os.environ['LD_LIBRARY_PATH']=lib

model_dir=os.path.dirname(__file__) # __file__=='/home/rusty/src/pescadero/model/model/local_config.py' 
data_dir=os.path.join(model_dir,"../../data")

class LocalConfig(object):
    dfm_bin_dir=os.path.join(dfm_root,'bin')
    mpi_bin_dir="" # just use what ever the module system put on PATH

    # Without this, srun assumes it can invoke dfm via openmpi, which dfm doesn't
    # recognize and you just get 16 simultaneous serial runs rather than 1 parallel
    # run.
    mpi_flavor='slurm'
    slurm_srun="srun"
    srun_args=["--mpi=pmi2"]
    num_procs=32

