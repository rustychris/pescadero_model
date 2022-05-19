#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 64
#SBATCH -N 1
#SBATCH --time 20-00:00:00

conda activate general

# Using local compile:
. /share/apps/intel-2019/bin/compilervars.sh intel64

PREFIX=/home/rustyh/src/dfm/t140737
export DFM_ROOT=$PREFIX/build/dfm/src/build_dflowfm/install

export PATH=$PREFIX/bin:$PATH
export LD_LIBRARY_PATH=$PREFIX/lib:$LD_LIBRARY_PATH
export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

uptime
mpiexec -info

python run_production_bmi.py -n 32 --three-d -p 2016-08-21,2016-08-21T06:00 --terrain asbuilt -f impaired -l 50 





