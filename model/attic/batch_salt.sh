#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH --mem-per-cpu 4G
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --time 5-00:00:00

# DFMROOT=/home/rustyh/src/dfm/delft3dfm_2021.01/lnx64
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$DFMROOT/lib

# srun --mpi=pmi2 $DFMROOT/bin/dflowfm --autostartstop flowfm.mdu --processlibrary $DFMROOT/share/delft3d/proc_def.def

conda activate general
python run_salt_2016_2017.py
