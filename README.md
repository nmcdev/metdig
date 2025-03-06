# Meteorological Diagnostic Tools (metdig)
## Detailed documentation can be found at：https://www.showdoc.com.cn/metdig

## Dependencies
Other required packages:
        'matplotlib < 3.6',
        'nmc_met_io <= 0.1.10.4',
        'metpy >= 1.0',
        'meteva > 1.3.*',
        'xarray <= 0.19.0 ',
        'cdsapi',
        'numba',
        'folium',
        'shapely < 1.8.0',
        'imageio',
        'numpy < 1.21',
        'protobuf<=3.20',
        'ipython',
        'pint < 0.20.0'
## Install
please install metdig under anaconda enviroment.
since Cartopy is hard to install, 
it is recommanded creating new env via conda and installing Cartopy first when the env is not complex yet.

``` install via pip
conda install -c conda-forge cartopy=0.19.0
pip install metdig
```
Using the following command to install packages:
```
  pip install git+git://github.com/nmcdev/metdig.git
```

or download the package and install:
```
  git clone --recursive https://github.com/nmcdev/metdig.git
  cd metdig
  python setup.py install
```

## Welcome to discuss in Issues
https://github.com/nmcdev/metdig/issues
