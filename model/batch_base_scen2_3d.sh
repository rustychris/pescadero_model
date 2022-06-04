#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
# Would like 64, but try 32
#SBATCH -n 32 
#SBATCH -N 1
#SBATCH --time 15-00:00:00

conda activate general

# Using local compile:
. /share/apps/intel-2019/bin/compilervars.sh intel64

PREFIX=/home/rustyh/src/dfm/t140737
export DFM_ROOT=$PREFIX/build/dfm/src/build_dflowfm/install

export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

uptime

python run_production_bmi.py -n 16 --three-d -p 2016long --terrain asbuilt -f impaired -s scen2 -l 100


