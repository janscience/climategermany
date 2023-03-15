import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from cruncdata import load_grids
from cities import load_cities
from world import load_shapes, plot_outlines
from IPython import embed

# load precipitation data:
file_path = 'ceda/cru_ts4.06.1901.2021.pre.dat.nc'
dates, lon, lat, data, unit = load_grids(file_path)

# cut out data from south-america:
lon_min = -85
lon_max = -33
lat_min = -56
lat_max = 16

year_min = np.datetime64('2012-01-01')

pre = data[dates > year_min, (lat[:-1] > lat_min) & (lat[:-1] < lat_max), (lon[:-1] > lon_min) & (lon[:-1] < lon_max)]
dates = dates[dates > year_min]
lat = lat[(lat > lat_min) & (lat < lat_max)]
lon = lon[(lon > lon_min) & (lon < lon_max)]

# average precipitation per month:
month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
               'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
months = np.arange(len(month_names))
pre_year = np.zeros((12, pre.shape[1], pre.shape[2]))
for m in months:
    pre_year[m] = np.mean(pre[m::12], 0)

# onset and offset of raining season:
thresh = np.mean(pre_year, 0)
rain_start = months[np.argmax((np.roll(pre_year, 2, 0) < thresh) & (np.roll(pre_year, 1, 0) < thresh) & (pre_year >= thresh) & (np.roll(pre_year, -1, 0) > thresh), 0)]
rain_end = months[np.argmax((np.roll(pre_year, 1, 0) >= thresh) & (pre_year >= thresh) & (np.roll(pre_year, -1, 0) < thresh) & (np.roll(pre_year, -2, 0) < thresh), 0)]
rain_start = np.ma.masked_where(np.ma.getmask(pre[0]), rain_start)
rain_end = np.ma.masked_where(np.ma.getmask(pre[0]), rain_end)

# load cities:
cities_lon, cities_lat, cities_names, cities_pop = \
    load_cities('maps/worldcities/worldcities.csv')
sel = (cities_lat > lat_min) & (cities_lat < lat_max) & \
      (cities_lon > lon_min) & (cities_lon < lon_max) & \
      (cities_pop > 1e5)
cities_names = np.array(cities_names)[sel]
cities_pop = cities_pop[sel]
cities_lat = cities_lat[sel]
cities_lon = cities_lon[sel]

# load shapes:
countries = load_shapes('maps/ne_10m_admin_0_countries.zip')
provinces = load_shapes('maps/ne_10m_admin_1_states_provinces.zip')
rivers = load_shapes('maps/ne_10m_rivers_lake_centerlines.zip')

# plot average precipitation at clicked location:
def onclick(event):
    if not event.inaxes:
        return
    if lon_min < event.xdata < lon_max and lat_min < event.ydata < lat_max:
        # index of coordinates:
        xi = np.argmin(np.abs(lon - event.xdata))
        yi = np.argmin(np.abs(lat - event.ydata))
        # next city:
        cities_dist = np.sqrt((cities_lon - event.xdata)**2 + (cities_lat - event.ydata)**2)
        ci = np.argmin(cities_dist)
        city = f'({cities_names[ci]})' if cities_dist[ci] < 0.5 else ''
        # plot:
        fig, ax = plt.subplots()
        ax.set_title(f'Precipitation at {event.xdata:.2f}, {event.ydata:.2f} {city}')
        ax.plot(months, pre_year[:, yi, xi], '-o', lw=2, zorder=10)
        for k in range(0, len(pre), 12):
            ax.plot(months, pre[k:k+12, yi, xi], '-', color='tab:blue',
                    lw=0.5, zorder=0)
        ax.axhline(thresh[yi, xi], color='k')
        ax.axvline(rain_start[yi, xi], color='g')
        ax.axvline(rain_end[yi, xi], color='r')
        ax.set_xticks(months) 
        ax.set_xticklabels(month_names)
        ax.set_ylabel(f'Precipitation [{unit}]')
        fig.show()

# plot map:
cont_kwargs = dict(levels=np.arange(13)-0.5, vmin=months[0]-0.2,
                   vmax=months[-1]+0.8, cmap='hsv', zorder=0)
countries_kwargs = dict(color='k', lw=0.5, zorder=30)
provinces_kwargs = dict(color='gray', lw=0.5, zorder=20)
rivers_kwargs = dict(color='b', lw=1, zorder=10)
cities_kwargs = dict(color='k', zorder=30)
fig, (ax1, ax2, cax) = plt.subplots(1, 3, 
                                    gridspec_kw=dict(width_ratios=(7, 7, 1)))
fig.canvas.mpl_connect('button_release_event', onclick)
ax1.set_title('Onset of rain season')
ax1.contourf(lon, lat, rain_start, **cont_kwargs)
plot_outlines(ax1, countries, **countries_kwargs)
plot_outlines(ax1, provinces, **provinces_kwargs)
plot_outlines(ax1, rivers, **rivers_kwargs)
ax1.scatter(cities_lon, cities_lat, s=cities_pop*0.2e-5, **cities_kwargs)
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')
ax1.set_xlim(lon_min, lon_max)
ax1.set_ylim(lat_min, lat_max)
ax1.set_aspect('equal')
ax2.set_title('Offset of rain season')
ax2.set_xlabel('Longitude')
ax2.yaxis.set_major_formatter(plt.NullFormatter())
ax2.set_xlim(lon_min, lon_max)
ax2.set_ylim(lat_min, lat_max)
ax2.set_aspect('equal')
ax2.get_shared_x_axes().join(ax1, ax2)
ax2.get_shared_y_axes().join(ax1, ax2)
cm = ax2.contourf(lon, lat, rain_end, **cont_kwargs)
plot_outlines(ax2, countries, **countries_kwargs)
plot_outlines(ax2, provinces, **provinces_kwargs)
plot_outlines(ax2, rivers, **rivers_kwargs)
ax2.scatter(cities_lon, cities_lat, s=cities_pop*0.2e-5, **cities_kwargs)
fig.colorbar(cm, cax=cax)
cax.set_yticks(months) 
cax.set_yticklabels(month_names) 
plt.show()
