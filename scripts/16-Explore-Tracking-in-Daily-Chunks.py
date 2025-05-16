#!/usr/bin/env python
# coding: utf-8

# # Explore Tracking in Daily Chunks

# In[1]:


import sys, os

import tobac
import datetime

import xarray as xr
import pandas as pd
import numpy as np

import pylab as plt
import seaborn as sns
import cartopy.crs as ccrs
import cartopy.feature as cf


# ## Arguments

# In[2]:


if 'launcher' in sys.argv[0]:
    main_dir = '/work/bb1376/user/fabian/data/oxford-hackathon/icon-hamlite/' 
    fname = f'{main_dir}/r2b9_lite_1224b/precip_features_thresh500/daily_precip_features_thresh500_20200602.nc'    
    interactive = True
else:
    fname = sys.argv[1]
    interactive = False


# ## Check if Previous Tracking was done

# In[3]:


date_str = fname.split('_')[-1].replace('.nc','')


# In[4]:


date = datetime.datetime.strptime(date_str, '%Y%m%d')
date_before = date - datetime.timedelta(days = 1)


# In[5]:


date_str_before = date_before.strftime('%Y%m%d')


# In[6]:


feature_file_before = fname.replace(date_str, date_str_before)
track_file_before = feature_file_before.replace('feature', 'track')


# In[7]:


if os.path.isfile( track_file_before ):
    use_prior_tracking = True
else:
    use_prior_tracking = False



# ## Open Data

# In[8]:


features = xr.open_dataset( fname ).to_dataframe()

if use_prior_tracking:
    prior_tracks = xr.open_dataset( track_file_before).to_dataframe()


# ## Linking Again

# In[9]:


dt = 15*60
dxy = 5e3

if not use_prior_tracking:
    tracks = tobac.linking_trackpy( features, None, dt, dxy, d_max = 5*dxy, time_cell_min=8*dt )
else:
    tracks = tobac.tracking.append_tracks_trackpy(
        prior_tracks, features,  dt, dxy, d_max = 5*dxy, time_cell_min=8*dt )


# ## Cleanup

# In[10]:


if use_prior_tracking:
    last_tmax = prior_tracks.time.max()

    mask = tracks['time'] > last_tmax
    tracks = tracks[mask]


# ## Output

# In[11]:


track_file = fname.replace('feature', 'track')

track_dir = os.path.dirname( track_file )

if not os.path.isdir( track_dir ):
    os.makedirs( track_dir )
tracks.to_xarray().to_netcdf(track_file)

