#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --time 15-00:00:00

conda activate general

### use stock compile for high partition
export DFM_ROOT=/home/rustyh/src/dfm/delft3dfm_2022.02/lnx64
export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

### Using local compile:
# . /share/apps/intel-2019/bin/compilervars.sh intel64
#  
# PREFIX=/home/rustyh/src/dfm/t140737
# export DFM_ROOT=$PREFIX/build/dfm/src/build_dflowfm/install
#  
# export PATH=$PREFIX/bin:$PATH
# export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
# export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

###

uptime

#python run_restart_debug_salt.py --suffix r001 --mdu data_2016long_3d_asbuilt_impaired_scen3-v003/flowfm.mdu --start 2017-01-07 --duration 1h

# when did salt balance go out? 2017-01-02 12:00:00? at least the worst is after that
python run_production_bmi.py --mdu data_2016long_3d_asbuilt_impaired_scen3-v003/flowfm.mdu --resume=2016-12-28T00:00 -p 2016long 


