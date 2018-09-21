import csv

data = []
with open("resources/airprox_reports_2000_to_2016.csv") as file:
    dataload = csv.reader(file, delimiter=",")
    for row in dataload:
        if len(row[0]) is not 0:
            data.append(row)
            print(row)

