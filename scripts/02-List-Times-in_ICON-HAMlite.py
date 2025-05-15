#!/usr/bin/env python
# coding: utf-8

# # List Times in ICON HAMlite

# ## Load Libraries 

# In[11]:


import sys, os

import cartopy.crs as ccrs
import cartopy.feature as cf

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

import pandas as pd

import scipy.ndimage
import seaborn as sns
#sns.set_context('talk')

from datetime import datetime


# In[2]:


from dask.diagnostics import ProgressBar


# ## Open Data 

# In[3]:


indir = '/work/bb1368/b381642/experiments/r2b9_lite_1224b_post/005deg'
fname = f'{indir}/r2b9_lite_1224b_atm_2d_vid_ml_*T000000Z.nc'


# In[6]:


dataset = xr.open_mfdataset( fname, chunks = 'auto' )

times = dataset.time


# ## Final Listing

# In[30]:


for t in times:
    formatted_strings = t.dt.strftime('%Y%m%dT%H%M')
    print( formatted_strings.data )

