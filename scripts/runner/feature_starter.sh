#!/bin/bash

runner=feature_runner.sh

l="../lists/icon-hamlite-timesteps.lst"

for c in ../config/config_precip[1-9]*c.json; do
#    for l in ../lists/icon-hamlite-timesteps.lst??; do 
        sbatch $runner $c $l
#    done
done
