import json

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.basemap import Basemap


def generate_map(*latlonpairs):
    fig = plt.figure(figsize=(18, 15))
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.85])
    ax.set_title("Cambridge Streetlights and Road Collisions")
    plt.gcf().set_size_inches([18, 10])

    m = Basemap(projection='merc', llcrnrlat=52.17, llcrnrlon=0.06,
                urcrnrlat=52.24, urcrnrlon=0.21, resolution='l')
    draw_fundamental_map_lines(m)

    for i in range(0, len(latlonpairs)):
        isline = (latlonpairs[i]["lines"] is True)
        size = 1.2
        color = "0"

        if "color" in latlonpairs[i]:
            size = 3
            color = latlonpairs[i]["color"]
            del latlonpairs[i]["color"]

        del latlonpairs[i]["lines"]
        plot_item(m, list(latlonpairs[i].values()), list(latlonpairs[i].keys()), isline, size, color)

    plt.show()


def plot_item(m, lat, lon, isline, size, color):
    x, y = m(lat, lon)
    width = 1 if isline is True else 0
    m.plot(x, y, marker="o", markersize=size, linewidth=width, color=color)


def draw_fundamental_map_lines(m):
    m.fillcontinents()
    m.drawparallels(np.arange(20, 70, 1), labels=[False, True, False, False], dashes=[1, 0], color='0.8')
    m.drawmeridians(np.arange(-100, 20, 5), labels=[True, False, False, True], dashes=[1, 0], color='0.8')


def process_streetlight_data():
    streetlight_raw_data = pd.read_csv("resources/streetlights_cam.csv", encoding="ISO-8859-1")
    streetlight_cols = streetlight_raw_data[["Latitude", "Longitude"]]
    streetlight_cols = streetlight_cols.values.astype("float32", copy=False)

    lats = streetlight_cols[:, [0]]
    lons = streetlight_cols[:, [1]]
    streetlights_data = {"lines": False}

    for i in range(0, len(lats)):
        streetlights_data[tuple(lats[i])[0]] = tuple(lons[i])[0]

    return streetlights_data


def process_bounds_data():
    with open("resources/cambridge_bounds.json", "r") as jsonfile:
        data = json.load(jsonfile)

    bounds_raw = data['features'][0]['geometry']['coordinates'][0]
    bounds_data = {"lines": True}

    for i in range(0, len(bounds_raw)):
        bounds_data[bounds_raw[i][1]] = bounds_raw[i][0]

    return bounds_data


def process_collision_data():
    with open("resources/RTC Location 2017_0.json", "r") as jsonfile:
        data = json.load(jsonfile)

    collision_raw = data['features']
    collision_data = {"lines": False, "color": "r"}

    for i in range(0, len(collision_raw)):
        lon = float(collision_raw[i]['geometry']['coordinates'][0])
        lat = float(collision_raw[i]['geometry']['coordinates'][1])
        collision_data[lat] = lon

    return collision_data


streetlights = process_streetlight_data()
bounds = process_bounds_data()
collisions = process_collision_data()

# generate_map(bounds, streetlights) weird anomalies in bounds data
generate_map(collisions, streetlights)
