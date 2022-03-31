#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 16
#SBATCH -N 1
#SBATCH --time 4-00:00:00

conda activate general
python run_production_bmi.py -n 16 -p 2016 -s scen3 -f impaired


