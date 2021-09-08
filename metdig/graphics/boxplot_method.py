import pandas as pd
import numpy as np
from metdig.graphics.lib.utility import kwargs_wrapper


@kwargs_wrapper
def boxplot_1D(ax, stda, medianline=False, label_gap=1, **kwargs):
    """[summary]

    Args:
        ax ([type]): [matplotlib 绘图对象]
        stda ([type]): [stda标准格式]
        medianline (bool, optional): [是否绘制中位数线]. Defaults to False.
        label_gap (int, optional): [横坐标的间隔]. Defaults to 1.

    """    
    # rain_x = list(map(lambda x: pd.to_datetime(x).strftime('%m月%d日%H时'), stda.stda.fcst_time.values))
    rain_x=[' ']*len(stda.stda.fcst_time.values)
    for ix in range(1,len(rain_x),label_gap):
        rain_x[ix]=pd.to_datetime(stda.stda.fcst_time.values[ix]).strftime('%m月%d日%H时')

    rain_y = stda.stda.get_value()
    img = ax.boxplot(np.transpose(rain_y), labels=rain_x, meanline=False, showmeans=True, showfliers=False, whis=(0, 100),
                            meanprops={'marker': None}, **kwargs)
    rain_mean = []
    rain_median = []
    for icurve_mean in img['means']:
        rain_mean.append(icurve_mean._y[0])
    curve_rain_mean = ax.plot(np.arange(1, len(rain_mean)+1), rain_mean, c=img['means'][1]._color,
                              linewidth=img['means'][1]._linewidth, linestyle='-',
                              label='mean')

    if (medianline):
        for icurve_median in img['medians']:
            rain_median.append(icurve_median._y[0])
        curve_rain_median = ax.plot(np.arange(1, len(rain_median)+1), rain_median, c=img['medians'][1]._color,
                                         linewidth=img['medians'][1]._linewidth, linestyle=img['medians'][1]._linestyle,
                                         label='median')

    rain_control = np.squeeze(rain_y[:, 0])
    curve_rain_control = ax.plot(np.arange(1, len(rain_control)+1), rain_control, c='black',
                                 linewidth=img['medians'][1]._linewidth, linestyle=img['medians'][1]._linestyle,
                                 label='control')

    ax.legend(fontsize=15, loc='best')

    return img