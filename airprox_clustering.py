import random

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from mpl_toolkits.basemap import Basemap
from sklearn.cluster import DBSCAN


def generate_map(plotitems):
    fig = plt.figure(figsize=(18, 15))
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.85])
    ax.set_title("Airprox Incidents 2000-2018?")
    plt.gcf().set_size_inches([18, 10])

    m = Basemap(projection='merc', lon_0=-4.36, lat_0=55, llcrnrlat=49, llcrnrlon=-8.5,
                urcrnrlat=59, urcrnrlon=5, resolution='l')
    draw_fundamental_map_lines(m)

    colmap = cm.get_cmap('gist_rainbow', 1000)

    for cluster in plotitems:
        col = colmap(random.uniform(0, 1))
        for key, val in dict(cluster).items():
            plot_lines(m, key, val, col)

    plt.show()


def dms_to_dd(val):
    seconds = 0
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


def plot_lines(m, lat, lon, col):
    x, y = m(lon, lat)
    m.plot(x, y, marker="o", color=col)


def draw_fundamental_map_lines(m):
    m.fillcontinents()
    m.drawparallels(np.arange(20, 70, 1), labels=[False, True, False, False], dashes=[1, 0], color='0.8')
    m.drawmeridians(np.arange(-100, 20, 5), labels=[True, False, False, True], dashes=[1, 0], color='0.8')


data = pd.read_csv("resources/airprox_reports_2000_to_2018.csv")
cols = data[["Latitude", "Longitude"]]
cols = cols.applymap(dms_to_dd)
cols = cols.values.astype("float32", copy=False)

eps = 11 / 6371.0088
db = DBSCAN(eps=eps, min_samples=4, algorithm='ball_tree', metric='haversine').fit(np.radians(cols))
num_clusters = len(set(db.labels_))
clusters = pd.Series([cols[db.labels_ == n] for n in range(num_clusters)])

generate_map(clusters)
