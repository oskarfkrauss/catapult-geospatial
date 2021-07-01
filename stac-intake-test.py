#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 28 11:48:00 2021

@author: oskarfkrauss

"""

%matplotlib inline

import matplotlib.pyplot as plt

import intake

from datetime import datetime

from IPython.display import Image

import json

print(intake.__version__)

url = 'https://raw.githubusercontent.com/sat-utils/sat-stac/master/test/catalog/catalog.json'
cat = intake.open_stac_catalog(url)
cat.metadata.keys()
list(cat)

subcat = cat['stac-catalog-eo']
list(subcat)

subcat1 = subcat['landsat-8-l1']
print(subcat1)

subcat2 = subcat['sentinel-s2-l1c']
print(subcat2)

items1 = list(subcat1)
items2 = list(subcat2)

subcat1.metadata
subcat2.metadata

# NOTE: would be good to have easy way for user to distinguish between catalogs and items
print(type(subcat1._stac_obj))
item1 = subcat1[items1[0]]

print(type(item1._stac_obj))

item1.metadata

Image(item1['thumbnail'].urlpath)

list(item1) # gets assets!

da = item1.B4.to_dask()

da

bands = ['green','red']
stack = item1.stack_bands(bands)
type(stack)

da = stack(chunks=dict(band=1, x=2048, y=2048)).to_dask()

da

da['band'] = bands
ds = da.to_dataset(dim='band')
ds

NDVI = (ds['green'] - ds['red']) / (ds['green'] + ds['red'])

subset = NDVI.isel(y=slice(6000,7000), x=slice(4500,5500))
subset.plot.imshow(cmap='BrBG', vmin=-1, vmax=1)

import satsearch

bbox = [-3.5, 55.77, -2.9, 56.1] # (min lon, min lat, max lon, max lat)
dates = '2020-07-01/2020-09-30'

URL='https://earth-search.aws.element84.com/v0'
results = satsearch.Search.search(url=URL,
                                  collections=['sentinel-s2-l2a-cogs'], # note collection='sentinel-s2-l2a-cogs' doesn't work
                                  datetime=dates,
                                  bbox=bbox,    
                                  sort=['<datetime'])


print('%s items' % results.found())
items = results.items() #item collection

items.save('my-s2-l2a-cogs.json')

catalog = intake.open_stac_item_collection(items) # catalog

type(catalog)

list(catalog)

item = catalog[list(catalog)[25]]

list(item) # assets

Image(item['thumbnail'].urlpath)

item.metadata

print(json.dumps(item.metadata['geometry'], indent=2))

item.metadata['eo:cloud_cover']

for i in range(len(catalog)):
    
    item = catalog[list(catalog)[i]]
    
    cc = item.metadata['eo:cloud_cover']
    
    if cc < 30:
        
        print(i)
        print(cc)
        print(item.metadata['date'].strftime('%d/%m/%Y'))
        
item = catalog[list(catalog)[1]]

Image(item['thumbnail'].urlpath)

bands = ['B04','B03','B02']
stack = item.stack_bands(bands)
type(stack)

da = stack(chunks=dict(band=1, x=2048, y=2048)).to_dask()
type(da)

RGB = da.isel(x=slice(5490,10980), y=slice(0, 5490))
RGB.plot.imshow(rgb = "band")


blu = da.isel(band = 0, x=slice(5490,10980), y=slice(0, 5490))
blu.plot.imshow()
plt.imsave('test_blue.png', blu, cmap = 'Blues')

gre = da.isel(band = 1, x=slice(5490,10980), y=slice(0, 5490))
gre.plot.imshow(cmap = 'Greens')
plt.imsave('test_green.png', gre, cmap = 'Greens')

red = da.isel(band = 2, x=slice(5490,10980), y=slice(0, 5490))
red.plot.imshow(cmap = 'Reds')
plt.imsave('test_red.png', red, cmap = 'Reds')
 
# Reorganize into xarray DataSet with common band names
da['band'] = bands
ds = da.to_dataset(dim='band')

type(da)
