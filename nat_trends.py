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


# import ggplot


def save_results_to_db():
    parser = MyParser()
    parser.feed(the_page)

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

    """
    m = Basemap(projection='stere', lon_0=-35, lat_0=55, lat_ts=55,
                width=5000000, height=2000000, resolution='l')
                hmm try a flat projection instead
                """
    m = Basemap(projection='merc',
                lon_0=-35, lat_0=55, lat_ts=55,
                llcrnrlat=40, llcrnrlon=-70,
                urcrnrlat=63, urcrnrlon=0,
                resolution='l')
    m.drawcoastlines()
    m.fillcontinents()

    m.drawparallels(np.arange(20, 70, 1), labels=[False, True, True, False], dashes=[1, 0], color='0.8')
    m.drawmeridians(np.arange(-100, 20, 1), labels=[True, False, False, False], dashes=[1, 0], color='0.8')

    ax.set_title("North Atlantic Tracks for " + str(day_of_month) + "." + str(month) + "." + str(year))
    plt.gcf().set_size_inches([18, 9])
    plt.show()


def remove_invalid_routes(data):
    for pos, item in enumerate(data):
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


dbconn, dbcurs = open_sqlite_db()

get_new = True
date = datetime.date.today()
day_of_month = date.day
month = date.month
year = date.year

results = get_day_results(dbcurs)
if len(results) is not 0:
    if len(results) is 5:
        dbcurs.execute("DELETE FROM nat WHERE day_of_month = ? AND month = ? AND year = ?", [day_of_month, month, year])
        print("Clearing partial results collected already for a re-run; deleted " + str(dbcurs.fetchall()) + " rows")
    else:
        # clarify the maxes we can expect? 10 westbound as of this morning???
        get_new = False
        print("Got " + str(len(results)) + " for today")

texts = []
url = "https://www.notams.faa.gov/common/nat.html"
epoch_time = int(time.time())
the_page = ""

if get_new is True:
    response = requests.get(url)
    the_page = response.content.decode("utf-8")


class MyParser(HTMLParser):
    def error(self, message):
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


if get_new is True:
    save_results_to_db()
    if len(texts) is not 0:
        print("Collected info for " + str(len(texts)) + " NAT tracks")

to_plot = get_day_results(dbcurs)
to_plot = [i[5] for i in to_plot]
generate_map(remove_invalid_routes(strip_levels(to_plot)))

dbconn.close()
