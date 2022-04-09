#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 64
#SBATCH -N 1
# Short run time because of maintenance.
#SBATCH --time 4-12:00:00

conda activate general
python run_production_bmi.py -n 64 --three-d -p 2016 -f impaired


