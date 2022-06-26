#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --time 20-00:00:00

conda activate general

# Using local compile:
. /share/apps/intel-2019/bin/compilervars.sh intel64
PREFIX=/home/rustyh/src/dfm/t140737
export DFM_ROOT=$PREFIX/build/dfm/src/build_dflowfm/install
export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH

# local compile on high queue is failing with illegal instruction.
# Use pre-compiled:
# export DFM_ROOT=/home/rustyh/src/dfm/delft3dfm_2022.02/lnx64

export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

uptime
cat /proc/cpuinfo | grep -e 'model name' | head -1

python run_production_bmi.py -n 16 --three-d -p 2016long --terrain asbuilt -f impaired --slr 0.6096 -l 30


