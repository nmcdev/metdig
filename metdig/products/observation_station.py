# -*- coding: utf-8 -*-

import os
import datetime
import numpy as np
import pandas as pd

from metdig.graphics.draw_compose import *
from metdig.graphics.plot_method import *
from metdig.graphics.bar_method import *
from metdig.graphics.barbs_method import *

def draw_blowup_sounding(pres,thta,theta,thetaes,u,v,extent=(260,400,1000,100),uv_barb_kwargs={},**pallete_kwargs):

    init_time = pd.to_datetime(pres['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    png_name = '{0:%Y}年{0:%m}月{0:%d}日{0:%H}_观测_{1:}_溃变理论诊断分析产品.jpg'.format(init_time,pres['id'].values[0],)
    obj=twod_compose(title='溃变理论诊断分析',description=pres.stda.description_point_obs(),png_name=png_name,kwargs=pallete_kwargs)
    obj.ax.xaxis.label.set_size(16)
    obj.ax.yaxis.label.set_size(16)
    obj.ax.tick_params(labelsize=14)

    obj.ax.plot(thta.stda.get_value(),pres.stda.get_value(),color='red',label='位温',linewidth=2)
    obj.ax.plot(theta.stda.get_value(),pres.stda.get_value(),color='green',label='假相当位温',linewidth=2)
    obj.ax.plot(thetaes.stda.get_value(),pres.stda.get_value(),color='purple',label='饱和相当位温',linewidth=2)
    obj.ax.barbs(thetaes.stda.get_value(), pres.stda.get_value(), u.stda.get_value(), v.stda.get_value(),
         color='black', length=6, fill_empty=False, sizes=dict(emptybarb=0.05),barb_increments={'half': 2, 'full': 4, 'flag': 20})
    obj.ax.legend(fontsize=15)
    obj.save()


def draw_obs_uv_tmp_rh_rain(tmp, u, v, rh, rain, wsp,
    tmp_plot_kwargs={},uv_barb_kwargs={},rh_plot_kwargs={},rain_bar_kwargs={},wsp_plot_kwargs={},
    **pallete_kwargs):

    init_time = pd.to_datetime(tmp['time'].values[0]).replace(tzinfo=None).to_pydatetime()
    title_left = '{} [{:.2f},{:.2f}]'.format(tmp['id'].values[0], tmp['lon'].values[0], tmp['lat'].values[0])
    title_right = '起报时间：{0:%Y}年{0:%m}月{0:%m}日{0:%H}时'.format(init_time)
    title_right = ''
    png_name = '观测_{0}_风_温度_相对湿度_降水_{1:%Y}年{1:%m}月{1:%d}日{1:%H}时起报.jpg'.format(tmp['id'].values[0], init_time)

    t2m_ylabel = '气温($^\circ$C) \n 风速(m s$^-$$^1$) \n 降水(mm)'
    rh_ylabel = '相对湿度(%)'
    uv_ylabel = '风'

    obj=time_series_left_right_bottom_compose(times=pd.to_datetime(tmp.stda.fcst_time.values),title_left=title_left, title_right=title_right,
        abel_leftax=t2m_ylabel, label_rightax=rh_ylabel, label_bottomax=uv_ylabel,
        png_name=png_name,kwargs=pallete_kwargs)

    # tmp
    curve_t2m = plot_1d(obj.ax_tmp, tmp, c='#FF6600', linewidth=3, label='气温',kwargs=tmp_plot_kwargs)
    obj.ax_tmp.set_xlim(tmp.stda.fcst_time.values[0] - pd.Timedelta(hours=1),tmp.stda.fcst_time.values[-1]+pd.Timedelta(hours=1))
    # obj.ax_tmp.set_ylim(np.min([np.floor(tmp.stda.get_value().min() / 5) * 5 - 2, 0]),np.max([np.ceil(tmp.stda.get_value().max() / 5) * 5, 40]))
    obj.ax_tmp.set_ylim(np.min([tmp.stda.get_value().min(),wsp.stda.get_value().min()])-2,
                        np.max([tmp.stda.get_value().max(), wsp.stda.get_value().max()])+2)

    # wsp
    curve_wsp = plot_1d(obj.ax_tmp, wsp, c='#282C5A', linewidth=3, label='风速',kwargs=wsp_plot_kwargs)

    if(rain is not None):
        # rain
        bars_rn = bar_1d(obj.ax_tmp, rain, width=0.1, color='#1E78B4', label='降水',kwargs=rain_bar_kwargs)

    if(rain is not None):
        bars_autolabel(obj.ax_tmp, bars_rn)
        # bars_autolabel(ax_tmp)

    # rh2m
    curve_rh = plot_1d(obj.ax_rh, rh, c='#067907', linewidth=3, label='相对湿度',kwargs=rh_plot_kwargs)
    # 10米风
    if(u is None or v is None):
        obj.ax_uv.set_axis_off()
    else:
        uv_barbs=barbs_2d(obj.ax_uv,u,v,xdim='fcst_time',ydim='lon',
                    fill_empty=True, color='gray', 
                    length=5.8, linewidth=1.5, kwargs=uv_barb_kwargs)
        
        obj.ax_uv.set_xlim(u.stda.fcst_time.values[0] - pd.Timedelta(hours=1), u.stda.fcst_time.values[-1] + pd.Timedelta(hours=1))
        for label in obj.ax_uv.get_xticklabels():
            label.set_rotation(30)
            label.set_horizontalalignment('center')
        
    # add legend
    obj.ax_tmp.legend(fontsize=15, loc='upper right')

    # save
    return obj.save()
    
