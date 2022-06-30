#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --time 20-00:00:00

conda activate general

python run_production_bmi.py -n 32 --three-d -p 2016-08-21,2016-08-26 --terrain asbuilt -f impaired -l 50





