
import cartopy.crs as ccrs

import metdig.metdig_graphics.lib.utl_plotmap as utl_plotmap


def city_text(ax, stda, transform=ccrs.PlateCarree(), alpha=1, size=13, **kwargs):
    utl_plotmap.add_city_values_on_map(ax, stda, alpha=alpha, size=size, **kwargs)
