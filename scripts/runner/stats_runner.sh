#!/bin/bash


#module load python3/unstable
source $HOME/.bashrc
source $HOME/.bash_mambainit
conda activate /home/b/b380352/proj/2025-05_oxford-hackathon/hackathon_env


cd ..
for c in config/config_precip[1-9]*json; do
#   sbatch $runner $c $l
#   python 07-Cell-Density-Maps.py $c 202006
   python 08-Plotting-Cloud-Size-Number-Distrib.py $c 202006
   python 12-Calculation-of-Lifetime-Histogramms.py $c 202006
done
cd -
