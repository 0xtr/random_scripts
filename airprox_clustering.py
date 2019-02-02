import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.basemap import Basemap


def generate_map():
    fig = plt.figure(figsize=(18, 15))
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.85])
    ax.set_title("Airprox Incidents 2000-2018?")
    plt.gcf().set_size_inches([18, 10])

    m = Basemap(projection='merc', lon_0=-4.36, lat_0=55, llcrnrlat=49, llcrnrlon=-8.5,
                urcrnrlat=59, urcrnrlon=5, resolution='l')
    draw_fundamental_map_lines(m)

    latlons = dict(zip(list(cols["Latitude"]), list(cols["Longitude"])))
    for key, val in latlons.items():
        plot_lines(m, key, val)

    plt.show()


def dms_to_dd(val):
    degrees = minutes = seconds = 0

    if "N" in val or "S" in val:
        degrees = val[0:2]
        minutes = val[2:4]
    else:
        degrees = val[1:3]
        minutes = val[3:5]

    dd = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
    if "S" in val or "W" in val:
        dd *= -1

    return dd


def process_lon_to_float(lon):
    val = ""
    if lon[5] is not "E":
        val += "-"

    lon = lon[2:5]
    val += lon[0] + "." + lon[1:3]
    return val


def plot_lines(m, lat, lon):
    x, y = m(lon, lat)
    m.plot(x, y, marker="+", color="black")


def draw_fundamental_map_lines(m):
    m.fillcontinents()
    m.drawparallels(np.arange(20, 70, 1), labels=[False, True, False, False], dashes=[1, 0], color='0.8')
    m.drawmeridians(np.arange(-100, 20, 5), labels=[True, False, False, True], dashes=[1, 0], color='0.8')


data = pd.read_csv("resources/airprox_reports_2000_to_2018.csv")
cols = data[["Latitude", "Longitude"]]
cols = cols.applymap(dms_to_dd)
generate_map()
