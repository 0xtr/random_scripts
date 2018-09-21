import re
from html.parser import HTMLParser
from unidecode import unidecode
import requests


def remove_non_ascii(text):
    return unidecode(text)


url = "https://www.notams.faa.gov/common/nat.html"
response = requests.get(url)
the_page = response.content.decode("utf-8")
texts = []


class MyParser(HTMLParser):
    def error(self, message):
        pass

    def handle_data(self, data):
        stripped = data.strip().replace("\n", " ")
        stripped = re.sub(r"REMARKS.+-", "", stripped)
        stripped = re.sub(r"PART .{2,5} OF .{2,5} PARTS-", "", stripped)
        if len(stripped) is not 0 and "PART" in stripped:
            stripped = re.sub(r"- {0,5}END OF PART .{2,5} OF .{2,5} PARTS.+", "", stripped).replace("-", "\n")
            texts.append(stripped)


parser = MyParser()
parser.feed(the_page)

for i in texts:
    print(i)
