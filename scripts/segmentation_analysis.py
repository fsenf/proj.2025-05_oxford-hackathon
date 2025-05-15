#!/usr/bin/env python


# ## Load Libraries
import os, sys
import numpy as np
import json

import sys

sys.path.append("../tools")

import input_data
import spacetools
import analysis


# ## Open Data

config_file = sys.argv[1]  # 'config_precip-cumsum50.json'
time_str = sys.argv[2]  # '2022-07-01'

with open(config_file, "r") as fp:
    conf = json.load(fp)
globals().update(conf)


# output

subname = f"{vname}_features_thresh{threshold}"

main_dir = "/work/bb1376/user/fabian/data/oxford-hackathon"
output_dir = f"/{main_dir}/{model}/{experiment}/{subname}"

outfile = f"{output_dir}/{subname}_{model}_{time_str}.nc"
print(f"... check for presence of output file: {outfile}")

if os.path.isfile(outfile):
    print(f"...{outfile} already exists ... do nothing")
    sys.exit(0)

print(f"... open {model} data")
if model == "icon-hamlite":
    dataset = input_data.input_icon_hamlite(
        time_str, experiment=experiment, vname=vname
    )

v = dataset[vname]  # .isel(lon = slice(0, None, 4), lat = slice(0, None, 4))

print("... do threshold calculation")
v_aligned = v.stack(cell=["lon", "lat"])
variable_threshold = analysis.threshold_calculation(vname, v_aligned, threshold)


print("... start segmentation")
# Segmentation
xfeat = analysis.segmentation_with_tobac(
    v, variable_threshold, threshold_target=threshold_target
)


# output
if not os.path.isdir(output_dir):
    os.makedirs(output_dir)

print(f"... output feature file to {outfile}")
xfeat.to_netcdf(outfile)
