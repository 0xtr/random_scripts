import datetime
import re
import time
from html.parser import HTMLParser
from unidecode import unidecode
import requests
import sqlite3


def remove_non_ascii(text):
    return unidecode(text)


dbconn = sqlite3.connect("nat_tracks.db")
dbcurs = dbconn.cursor()
dbcurs.execute("CREATE TABLE IF NOT EXISTS nat (day_of_month int, month int, year int, epochtime int, details text)")

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
        print("Nothing to collect for today; already got 5+9 tracks")
        exit(1)

texts = []
url = "https://www.notams.faa.gov/common/nat.html"
response = requests.get(url)
the_page = response.content.decode("utf-8")
epoch_time = int(time.time())


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


parser = MyParser()
parser.feed(the_page)

for i in texts:
    dbcurs.execute("INSERT INTO nat VALUES (?,?,?,?,?)", [day_of_month, month, year, epoch_time, i])
    dbconn.commit()

dbconn.close()

if len(texts) is not 0:
    print("Collected info for " + str(len(texts)) + " NAT tracks")


