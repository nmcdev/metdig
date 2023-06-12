import os
import webbrowser


def easy_sel_point(zoom_start=5, openinwebbrowser=False):
    '''
    选择获取经纬度
    '''
    
    try:
        import folium
    except:
        raise Exception("folium not exists, please install folium first, such as: pip install folium")
    
    m = folium.Map(
        location=[35, 108],
        zoom_start=zoom_start,
        tiles='http://webrd02.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=7&x={x}&y={y}&z={z}',
        attr='default',
        control_scale=True,

    )

    m.add_child(folium.LatLngPopup())

    if openinwebbrowser:
        htmlpath = 'easy_sel_point.html'
        htmlpath = os.path.expanduser('~') + '/easy_sel_point.html'
        m.save(htmlpath)  # 保存到本地
        webbrowser.open(htmlpath)  # 在浏览器中打开

    return m


if __name__ == '__main__':

    easy_sel_point()

    pass
