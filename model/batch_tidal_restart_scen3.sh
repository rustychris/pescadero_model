#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --time 3-00:00:00

conda activate general
python run_restart_highres.py --mdu data_2016_2d_asbuilt_impaired_scen3-v001/flowfm.mdu --start "2016-08-04T00:00" --duration 36h --suffix rtidal



