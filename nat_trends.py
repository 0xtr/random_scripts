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

date = datetime.date.today()
day_of_month = date.day
month = date.month
year = date.year
"""
def remove_non_ascii(text):
    return unidecode(text)


dbconn = sqlite3.connect("resources/nat_tracks.db")
dbcurs = dbconn.cursor()
dbcurs.execute("CREATE TABLE IF NOT EXISTS nat ("
               "direction text, "
               "day_of_month int, month int, year int, "
               "epochtime int, "
               "details text)")

get_new = True
date = datetime.date.today()
day_of_month = date.day
month = date.month
year = date.year

dbcurs.execute("SELECT * FROM nat WHERE day_of_month = ? AND month = ? AND year = ?", [day_of_month, month, year])
results = dbcurs.fetchall()
if len(results) is not 0:
    if len(results) is 5:
        dbcurs.execute("DELETE FROM nat WHERE day_of_month = ? AND month = ? AND year = ?", [day_of_month, month, year])
        print("Clearing partial results collected already for a re-run; deleted " + str(dbcurs.fetchall()) + " rows")
    else:
        # clarify the maxes we can expect? 10 westbound as of this morning???
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
    parser = MyParser()
    parser.feed(the_page)

    for i in texts:
        direction = "WEST" if "EAST LEVELS NIL" in i else "EAST"
        dbcurs.execute("INSERT INTO nat VALUES (?, ?,?,?,?,?)", [direction, day_of_month, month, year, epoch_time, i])
        dbconn.commit()

dbconn.close()

if len(texts) is not 0:
    print("Collected info for " + str(len(texts)) + " NAT tracks")

# TODO:
# text processing
# mapping
"""

fig = plt.figure(figsize=(18, 15))
ax = fig.add_axes([0.1, 0.1, 0.8, 0.8])

m = Basemap(projection='stere', lon_0=-35, lat_0=55, lat_ts=55,
            width=5000000, height=2000000, resolution='l', area_thresh=10000)
m.drawcoastlines()
m.fillcontinents()

m.drawparallels(np.arange(20, 70, 1))
m.drawmeridians(np.arange(-100, 20, 1))

ax.set_title("North Atlantic Tracks for " + str(day_of_month) + "/" + str(month) + "/" + str(year))
plt.show()
