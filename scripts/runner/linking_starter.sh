#!/bin/bash

runner=linking_runner.sh


for c in ../config/config_precip[1-9]*json; do
#   sbatch $runner $c $l
   bash $runner $c $l
done
