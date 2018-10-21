import datetime
import re
import time
from html.parser import HTMLParser
from unidecode import unidecode
import requests
import sqlite3
from mpl_toolkits.basemap import Basemap
import numpy as np
import matplotlib.pyplot as plt


# Python wheels for basemap and pyproj are available at:
# https://www.lfd.uci.edu/~gohlke/pythonlibs/
# for windows, at least


def save_results_to_db(page):
    epoch_time = int(time.time())
    parser = MyParser()
    parser.feed(page)

    for i in texts:
        direction = "WEST" if "EAST LEVELS NIL" in i else "EAST"
        dbcurs.execute("INSERT INTO nat VALUES (?, ?,?,?,?,?)", [direction, day_of_month, month, year, epoch_time, i])
        dbconn.commit()


def remove_non_ascii(text):
    return unidecode(text)


def strip_levels(items):
    for pos, item in enumerate(items):
        item = item.split("EAST LVLS")[0]
        items[pos] = item
    return items


def generate_map(plotitems):
    fig = plt.figure(figsize=(18, 15))
    ax = fig.add_axes([0.05, 0.05, 0.9, 0.85])
    ax.set_title("North Atlantic Tracks for " + str(day_of_month) + "." + str(month) + "." + str(year))
    plt.gcf().set_size_inches([18, 9])

    m = Basemap(projection='lcc', width=14000000, height=10000000,
                lon_0=-35, lat_0=55, lat_ts=55, llcrnrlat=35, llcrnrlon=-60,
                urcrnrlat=61, urcrnrlon=5, resolution='l')
    draw_fundamental_map_lines(m)
    draw_fir_boundaries(m)

    for item in plotitems:
        col = get_color(item.letter)
        mark = get_marker(item.direction)
        item.lons = [-x for x in item.lons]

        x, y = m(item.lons, item.lats)
        m.plot(x, y, marker=mark, color=col)
        draw_start_end_markers(item, mark, m)
        # TODO: investigate why some routes don't have an end marker?

    plt.show()


def get_latlon_for_marker(marker):
    # TODO: magic
    print("Hello " + marker)


def draw_fir_boundaries(m):
    airspace_name_to_colors = {
        "UK": "xkcd:greyish blue",
        "shanwick": "xkcd:mint green",
        "gander": "xkcd:lime",
        "santamaria": "xkcd:green yellow"
    }
    # key airspace name to a value tuple of lat/lon arrays
    airspace_name_to_latlons = {
        "UK": [[65, 61, 61, 61, 54.8, 54, 51, 51, 45, 45, 43, 42, 36],
               [0, 0, -5, -10, -10, -15, -15, -8, -8, -13, -13, -15, -15]],
        "shanwick": [[61, 61, 61, 61, 61, 45, 45, 45, 45, 45, 45, 45],
                     [-10, -15, -20, -25, -30, -30, -25, -20, -15, -10, -5, 0]],
        "gander": [
            [45, 45, 45, 44.5, 44.5, 44.5, 49, 53, 57, 61, 65, 65, 63, 60, 58.5, 58.5, 62.4, 65, 68, 65, 62.4, 61],
            [-30, -35, -40, -40, -45, -51, -51, -54, -59, -63, -63, -60, -55, -51.5, -50, -43, -39, -36, -28, -36, -39,
             -30]],
        "santamaria": [[44.5, 27, 22.5, 17, 24, 30],
                       [-40, -40, -40, -37.5, -25, -25]],
        "newyork": [[44.5, 44.5, 41.8],
                    [-50, -52, -67]]
    }

    for key, val in airspace_name_to_latlons.items():
        x, y = m(val[1], val[0])
        m.plot(x, y, marker="", color=airspace_name_to_colors.get(key))

    # TODO:
    # new york
    # nota/sota boundaries

    # TODO: make cleaner as more added, find best format to avoid cluttering map, angle text
    # compress into loop etc
    x, y = m(-11, 53)
    plt.annotate("SHANNON FIR", xy=(x, y))
    x, y = m(-14, 56)
    plt.annotate("NOTA", xy=(x, y))
    x, y = m(-12.5, 50)
    plt.annotate("SOTA", xy=(x, y))
    x, y = m(-29, 46)
    plt.annotate("SHANWICK OCA", xy=(x, y))
    x, y = m(-39, 45.5)
    plt.annotate("GANDER OCEANIC CTA", xy=(x, y))


def draw_fundamental_map_lines(m):
    m.fillcontinents()
    m.drawparallels(np.arange(20, 70, 1), labels=[False, True, False, False], dashes=[1, 0], color='0.8')
    m.drawmeridians(np.arange(-100, 20, 5), labels=[True, False, False, True], dashes=[1, 0], color='0.8')


def draw_start_end_markers(item, mark, m):
    if len(item.lons) > 0:
        x_beg, y_beg = m(item.lons[0], item.lats[0])
        x_end, y_end = m(item.lons[len(item.lons) - 1], item.lats[len(item.lats) - 1])
        start_align = "left" if mark is "<" else "right"
        end_align = "right" if mark is "<" else "left"
        plt.text(x_beg, y_beg, item.from_item, fontweight='bold', va='bottom', ha=start_align)
        plt.text(x_end, y_end, item.to_item, va='center', ha=end_align)


def get_marker(direction):
    return "<" if direction is "WEST" else ">"


def get_color(letter):
    return "xkcd:turquoise" if re.match("[A-L]", letter) else "xkcd:magenta"


def remove_invalid_routes(data):
    for item in data[:]:
        if not re.match(r"[A-Z] [A-Z]{5} .+", item):
            print("Invalid entry removed: " + item)
            data.remove(item)
    return data


def open_sqlite_db():
    conn = sqlite3.connect("resources/nat_tracks.db")
    curs = conn.cursor()
    curs.execute("CREATE TABLE IF NOT EXISTS nat ("
                 "direction text, "
                 "day_of_month int, month int, year int, "
                 "epochtime int, "
                 "details text)")
    return conn, curs


def get_day_results(curs):
    dbcurs.execute("SELECT * FROM nat WHERE day_of_month = ? AND month = ? AND year = ?", [day_of_month, month, year])
    return curs.fetchall()


def process_plot_data(to_process):
    newplots = []
    for i in to_process:
        print("processing " + str(i))
        fragments = i.split(" ")
        p = PlotItem(fragments)

        for frag in fragments:
            if "/" in frag:
                nums = frag.split("/")
                lon = int(nums[1])
                lat = float(nums[0][:2] + "." + nums[0][2:]) if len(frag) is 7 else int(nums[0])
                p.lats.append(lat)
                p.lons.append(lon)

        newplots.append(p)

    return newplots


def is_a_marker(fragment):
    return re.match("[A-Z]{5}", fragment)


class PlotItem:
    from_item = []
    to_item = []
    lats = []
    lons = []
    letter = ''
    direction = ''

    def __init__(self, fragments):
        self.letter = fragments[0]
        self.from_item = fragments[1]
        self.direction = "WEST" if re.match("[A-L]", fragments[0]) else "EAST"

        fraglen = len(fragments)
        # TODO: handle 2nd marker when coords transcribed for them
        if is_a_marker(fragments[fraglen - 2]):
            self.to_item = fragments[fraglen - 2]

        self.lats = list()
        self.lons = list()


class MarkerLoader:
    _file_location = "resources/entry_points_to_latlons.txt"
    _marker_data = {}
    _marker_list = []
    _unique_latlons = []

    def __init__(self):
        with open(self._file_location) as fi:
            contents = list(map(lambda x: x.replace("\n", ""), fi.readlines()))

        temp = list(map(lambda sp: sp.split(","), contents))
        for item in temp:
            assert len(item) is 3
            i1 = float(item[1])
            i2 = float(item[2])
            if [i1, i2] in self._unique_latlons:
                print("Marker for " + item[0] + " already recorded in list. Check for accuracy.")
                exit(1)

            self._marker_data[item[0]] = [i1, i2]
            self._marker_list.append(item[0])
            self._unique_latlons.append([i1, i2])

    def get_marker_data(self):
        return self._marker_data

    def get_all_marker_names(self):
        return self._marker_list


class MyParser(HTMLParser):
    def error(self, message):
        print(message)
        pass

    def handle_data(self, data):
        data = data.strip().replace("\n", " ")
        data = re.sub(r"REMARKS.+-", "", data)
        data = re.sub(r"PART .{2,5} OF .{2,5} PARTS-", "", data)

        if len(data) is not 0 and "PART" in data:
            data = re.sub(r"- {0,5}END OF PART .{2,5} OF .{2,5} PARTS.+", "", data)

            if "-" in data:
                splits = data.split("- ")
                for s in splits:
                    texts.append(s.lstrip(" "))
            else:
                texts.append(data.lstrip(" "))


dbconn, dbcurs = open_sqlite_db()

get_new = True
date = datetime.date.today()
day_of_month = date.day
month = date.month
year = date.year

results = get_day_results(dbcurs)
if len(results) is not 0:
    dbcurs.execute("DELETE FROM nat WHERE day_of_month = ? AND month = ? AND year = ?", [day_of_month, month, year])
    print("Clearing partial results collected already for a re-run; deleted " + str(dbcurs.rowcount) + " rows")

if get_new is False:
    print("heatmap NYI")
    pass

texts = []
url = "https://www.notams.faa.gov/common/nat.html"
the_page = requests.get(url).content.decode("utf-8")

save_results_to_db(the_page)
if len(texts) is not 0:
    print("Collected info for " + str(len(texts)) + " tracks")

load_markers = MarkerLoader()
to_plot = get_day_results(dbcurs)
to_plot = [i[5] for i in to_plot]
to_plot = remove_invalid_routes(strip_levels(to_plot))
generate_map(process_plot_data(to_plot))

dbconn.close()
