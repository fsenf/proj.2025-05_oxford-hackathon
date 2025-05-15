#!/usr/bin/env python
# coding: utf-8

# # Linking of Individual Features

# ## Libs Sections 

# In[1]:


import xarray as xr
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
#import seaborn as sns
#sns.set_context('talk')
import cartopy.crs as ccrs
import cartopy.feature as cf


import glob

import tobac
import sys, os
import json



# ## Arguments

# In[2]:


if 'launcher' in sys.argv[0]:
    config_file = '../scripts/config/config_precip100.json'
    date = '202006'
    interactive = True
else:
    config_file = sys.argv[1]
    date = sys.argv[2]
    interactive = False


# ## Configuration

# In[3]:


with open(config_file, "r") as fp:
    conf = json.load(fp)
globals().update(conf)


# ## Input Data 

# In[4]:


main_dir = "/work/bb1376/user/fabian/data/oxford-hackathon"
subname = f"{vname}_features_thresh{threshold}"

input_dir = f"/{main_dir}/{model}/{experiment}/{subname}"

infile =  f'{input_dir}/monthly_{subname}_{date}.nc'


# In[5]:


min_vlist = ['frame','hdim_1','hdim_2', 'time']
all_feats = xr.open_dataset( infile )

selected_feats = all_feats[min_vlist].to_dataframe()


# In[6]:


features = selected_feats # [selected_feats["frame"] < 100]

# features = xr.open_dataset( infile )
# features = features.isel(index=slice(0,100000,10)).to_dataframe()


# ## Dummy Data

# In[15]:


dummy = None


# ## Linking

# In[9]:


# Keyword arguments for linking step:
parameters_linking={}
parameters_linking['method_linking']='predict'
parameters_linking['adaptive_stop']=0.2
parameters_linking['adaptive_step']=0.95
parameters_linking['extrapolate']=0
parameters_linking['order']=1
parameters_linking['subnetwork_size']=100
parameters_linking['memory']=3
parameters_linking['time_cell_min']=30*60
parameters_linking['method_linking']='predict'
parameters_linking['v_max']=30


# In[10]:


#  %%time

dt = 15*60
dxy = 5000.
tracks = tobac.linking_trackpy(features,dummy,dt=dt,dxy=dxy,**parameters_linking)


# ## Output

# In[11]:


xtracks = tracks.to_xarray()


# In[12]:


xtracks = xr.merge([xtracks,all_feats])


# In[13]:


outdir = f"/{main_dir}/{model}/{experiment}/tracks"

if not os.path.isdir( outdir ):
    os.makedirs( outdir )

newsub = subname.replace('feature', 'track')
outfile = f'{outdir}/monthly_{newsub}_{date}.nc'

delayed = xtracks.to_netcdf( outfile, compute = False  )


# In[14]:


from dask.diagnostics import ProgressBar
with ProgressBar():
    delayed.compute()


# In[ ]:




