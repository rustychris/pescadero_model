#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --time 20-00:00:00

conda activate general
export DFM_ROOT=/home/rustyh/src/dfm/delft3dfm_2022.02/lnx64
export LD_LIBRARY_PATH=$DFM_ROOT/lib:$LD_LIBRARY_PATH

uptime

python run_production_bmi.py -n 16 --three-d -p 2016long --terrain asbuilt -f impaired -l 30





