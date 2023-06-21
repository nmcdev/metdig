import numpy as np

import cartopy.crs as ccrs

import metdig.graphics.lib.utility as utl
import metdig.graphics.cmap.cm as cm_collected
from  metdig.graphics.lib.utility import kwargs_wrapper

@kwargs_wrapper
def scatter_2d(ax, stda, xdim='lon', ydim='lat',
                  add_colorbar=True, cb_pos='bottom', cb_ticks=None, cb_label=None,
                  levels=np.arange(-40,40), cmap='ncl/BlueYellowRed', extend='both',isLinear=False,
                  transform=ccrs.PlateCarree(), alpha=1,
                  colorbar_kwargs={},s=1,size_changable=True, **kwargs):
    """[graphics层绘制scatter平面图通用方法]

    Args:
        ax ([type]): [description]
        stda ([type]): [u矢量 stda标准格式]
        xdim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lon'.
        ydim (type, optional): [stda维度名 member, level, time dtime, lat, lon或fcst_time]. Defaults to 'lat'.
        add_colorbar (bool, optional): [是否绘制colorbar]. Defaults to True.
        cb_pos (str, optional): [colorbar的位置]. Defaults to 'bottom'.
        cb_ticks ([type], optional): [colorbar的刻度]. Defaults to None.
        cb_label ([type], optional): [colorbar的label，如果不传则自动进行var_cn_name和var_units拼接]. Defaults to None.
        levels ([list], optional): [description]. Defaults to None.
        cmap (str, optional): [description]. Defaults to 'jet'.
        extend (str, optional): [description]. Defaults to 'both'.
        isLinear ([bool], optional): [是否对colors线性化]. Defaults to False.
        transform ([type], optional): [stda的投影类型，仅在xdim='lon' ydim='lat'时候生效]. Defaults to ccrs.PlateCarree().
        alpha (float, optional): [description]. Defaults to 1.
        s=1 (float, optional): [散点大小]. Defaults to 1.
        size_changable ([bool],optional):[散点大小是否与数值随动]，Defaults to True.
    Returns:
        [type]: [绘图对象]
    """
    x = stda.stda.get_dim_value(xdim)
    y = stda.stda.get_dim_value(ydim)
    z = stda.stda.get_value(ydim, xdim)

    cmap, norm = cm_collected.get_cmap(cmap, extend=extend, levels=levels,isLinear=isLinear)
    if transform is None or (xdim != 'lon' and ydim != 'lat'):
        if not size_changable:
            img = ax.scatter(x, y, s, norm=norm, cmap=cmap,c=z, alpha=alpha, **kwargs)
        else:
            img = ax.scatter(x, y, z*s, norm=norm, cmap=cmap,c=z, alpha=alpha, **kwargs)
    else:
        if not size_changable:
            img = ax.scatter(x, y, s, norm=norm, cmap=cmap,c=z, alpha=alpha, **kwargs)
        else:
            img = ax.scatter(x, y, z*s, norm=norm, cmap=cmap,c=z, transform=transform, alpha=alpha, **kwargs)


    if add_colorbar:
        try:
            cb_label = '{}({})'.format(stda.attrs['var_cn_name'], stda.attrs['var_units']) if not cb_label else cb_label
        except:
            print('输入变量请添加"var_cn_name"属性和"var_units"属性')
        utl.add_colorbar(ax, img, ticks=cb_ticks, pos=cb_pos, extend=extend, label=cb_label, kwargs=colorbar_kwargs)
    
    return img
