#!/usr/bin/python3

import re
from xml.etree import ElementTree as ET
import base64

data = open("full-emoji-list.html", 'rb').read()

start = b"<table"
end = b"</table>"
row_start = b"<tr>"
row_end = b"</tr>"

a = data[data.find(start) : data.find(end) + len(end)]
a = a[19:-len(end)]

rows = []
while b"<tr>" in a:
	rows.append(a[a.find(row_start) : a.find(row_end) + len(row_end)])
	a = a[a.find(row_end) + len(row_end) : ]

# get headers
headers_raw = rows[0]
headers = re.findall("<.*'>(.*?)</a></th>", headers_raw.decode("utf8"))
headers[0] = "Id"
headers[5] = "Google"

headers = [
	headers[1], # Unicode code
	headers[4], # apple image
	headers[15] # description
]

parsed_rows = map(
	lambda x: re.findall(b"<td.*?>(.*?)</td>", x),
	rows[1:]
)

# is it really a row or just headers
parsed_rows = filter(
	lambda x: x,
	parsed_rows
)

raw_data = [
	[
		i[1], # Unicode code
		i[4], # apple image
		i[15] # description
	]
	for i in parsed_rows
]

# only images that exist for apple. not '-'
raw_data = filter(
	lambda x: x[1] != b'\xe2\x80\x94',
	raw_data
)

data = [
	[
		re.findall(b"name='(.*?)'", i[0])[0],
		re.findall(b"src='data:image/png;base64,(.*?)'>", i[1])[0],
		i[2]
	]
	for i in raw_data
]

data = [
	[
		i[0].decode("utf8"),
		base64.decodebytes(i[1]),
		i[2].decode("utf8")
	]
	for i in data
]

csv = open("/home/me/Projects/Whatsapp/emoji/description.csv", 'w')

for i in data:
	csv.write("%s,%s\n" % (i[0], i[2]))
	# add image
	open("/home/me/Projects/Whatsapp/emoji/images/%s.png" % i[0], 'wb').write(i[1])

csv.close()