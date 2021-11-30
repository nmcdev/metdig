# 天气学诊断分析工具(Meteorological Diagnostic Tools, metdig)
## 详细使用说明请参考该网站内容：https://www.showdoc.com.cn/metdig

## Dependencies
Other required packages:
- 请在anaconda环境下安装，并确保matplotlib、meteva符合以下版本需求
- matplotlib
- cartopy >= 0.19.0
- metpy >=1.0
- meteva >=1.3.*
- cdsapi
- nmc_met_io
- numba
- folium
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

## 欢迎在Issues留言交流
https://github.com/nmcdev/metdig/issues
