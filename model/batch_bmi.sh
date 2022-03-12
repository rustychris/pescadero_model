#!/bin/bash -l
#SBATCH --job-name pesca
#SBATCH -o slurm_out-%j.output
#SBATCH -e slurm_out-%j.output
#SBATCH --partition high2
#XXXSBATCH --mem-per-cpu 4G
#SBATCH -n 32
#SBATCH -N 1
#SBATCH --time 10-00:00:00

conda activate general
python run_production_bmi.py -n 32

