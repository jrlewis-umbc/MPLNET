import pycurl
import certifi
import netCDF4
from netCDF4 import Dataset
import numpy as np
import pandas as pd

# Download netcdf-4 file using pycurl, read file, and plot
local_file = "/mplnet_download_" + YYYY + MM + DD + ".nc4"
try: 
	with open(local_file, 'wb') as f:
		c = pycurl.Curl()
		c.setopt(c.URL, result)
  	c.setopt(c.WRITEDATA, f)
		c.setopt(c.CAINFO, certifi.where())
		c.perform()
		c.close()
except pycurl.error as e:
    print(f"Error during download: {e}")

file_link = 'https://mplnet.gsfc.nasa.gov/download?version=V3&level=L1&product=NRB&site=' + site + '&year=' + YYYY + '&month=' + MM + '&day=' + DD + '&var=nrb,vol_depol_ratio'
file_id = Dataset(local_file)
time = np.array(file_id.variables['time'][:])
time_obj = pd.to_datetime(time, unit='D', origin='julian') 
altitude = np.array(file_id.variables['altitude'][:,:])
nrb = np.array(file_id.variables['nrb'][0,:,:])
nrb = nrb.T
vdr = np.array(file_id.variables['vol_depol_ratio'][0,:,:])
vdr = vdr.T
