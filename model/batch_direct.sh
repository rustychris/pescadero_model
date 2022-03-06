#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#REMSBATCH --mem-per-cpu 4G
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --time 10-00:00:00

DFMROOT=/home/rustyh/src/dfm/delft3dfm_2022.02/lnx64
export LD_LIBRARY_PATH=$DFMROOT/lib:/share/apps/mpfr-3.1.2/lib:/share/apps/slurm-20.11.8/18.04/lib

srun --mpi=pmi2 $DFMROOT/bin/dflowfm --autostartstop flowfm.mdu --processlibrary $DFMROOT/share/delft3d/proc_def.def
