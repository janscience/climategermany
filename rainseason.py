import numpy as np
import matplotlib.pyplot as plt
from cruncdata import load_grids
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

# plot average precipitation at clicked location:
def onclick(event):
    if lon_min < event.xdata < lon_max and lat_min < event.ydata < lat_max:
        xi = np.argmin(np.abs(lon - event.xdata))
        yi = np.argmin(np.abs(lat - event.ydata))
        fig, ax = plt.subplots()
        ax.set_title(f'Precipitation at {event.xdata:.2f}, {event.ydata:.2f}')
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
                   vmax=months[-1]+0.8, cmap='hsv')
fig, (ax1, ax2, cax) = plt.subplots(1, 3, 
                                    gridspec_kw=dict(width_ratios=(7, 7, 1)))
fig.canvas.mpl_connect('button_press_event', onclick)
ax1.set_title('Onset of rain season')
ax1.contourf(lon, lat, rain_start, **cont_kwargs)
ax1.set_xlabel('Longitude')
ax1.set_ylabel('Latitude')
ax1.set_aspect('equal')
ax2.set_title('Offset of rain season')
ax2.set_xlabel('Longitude')
ax2.yaxis.set_major_formatter(plt.NullFormatter())
ax2.set_aspect('equal')
ax2.get_shared_x_axes().join(ax1, ax2)
ax2.get_shared_y_axes().join(ax1, ax2)
cm = ax2.contourf(lon, lat, rain_end, **cont_kwargs)
fig.colorbar(cm, cax=cax)
cax.set_yticks(months) 
cax.set_yticklabels(month_names) 
plt.show()
