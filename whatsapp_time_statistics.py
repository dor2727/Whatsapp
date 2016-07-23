import re
from dateutil.parser import parse as dateutil_parse_date
import matplotlib.pyplot as plt
from datetime import datetime

DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

SUPPORTED_HOURS_DELTA = [0.5, 1, 2]

def read_data(file_name='w'):
	f = open(file_name, 'rb')
	a = f.read()
	f.close()
	return a

def parse_lines(data):
	b = [i.decode("utf8") for i in data.splitlines()]

	# c = [i for i in b if u':' in i]
	# cc = [i for i in b if u':' not in i]

	# for i in range(len(cc)):
	# 	f = open("Projects/Whatsapp/%d" % i, 'wb')
	# 	f.write(cc[i].encode("utf8"))
	# 	f.close()

###### TIME PARSING ######
def get_full_dates(data=None):
	if not data:
		data = read_data()

	return re.findall(u"\d{1,2}/\d{1,2}/\d\d, \d\d:\d\d - ", data)

#### DATES ####
def get_dates(data=None):
	if not data:
		data = get_full_dates()
	raw = [re.findall("^(\d{1,2}/\d{1,2}/\d\d), ", i)[0] for i in data]
	# dates in datetime format
	return [dateutil_parse_date(i) for i in raw]

def get_filtered_dates(data=None, start=None, end=None):
	if not data:
		data = get_dates()

	if start and end:
		return [i for i in data if start <= i < end]
	elif start and not end:
		return [i for i in data if start <= i      ]
	elif not start and end:
		return [i for i in data if          i < end]
	else:
		return [i for i in data if          i      ]

def get_weekdays(data=None, start=None, end=None):
	data = get_filtered_dates(data, start, end)

	weekdays = [0]*7
	for i in data:
		weekdays[i.weekday()] += 1
	
	return weekdays

def get_months(data=None, start=None, end=None):
	data = get_filtered_dates(data, start, end)

	months = [0]*12
	for i in data:
		months[i.month - 1] += 1

	return months

def get_creation_date(data=None):
	if not data:
		data = get_dates()

	return data[0]

def get_last_date(data=None):
	if not data:
		data = get_dates()

	return data[-1]

#### hours ####
def get_raw_minutes(data=None):
	if not data:
		data = get_full_dates()
	raw = [re.findall(", (\d\d:\d\d) - ", i)[0] for i in data]
	# convert hh:mm to minutes (02:15 -> 135)
	return [int(i[:2]) * 60 + int(i[-2:]) for i in raw]

def get_minutes(data=None, delta=0.5):
	if not data:
		data = get_raw_minutes()
	if delta not in SUPPORTED_HOURS_DELTA:
		raise Exception("Unsupported hour delta")
	
	# create a list of 48 counters for each half an hour
	minutes_groups = [0] * int(24. / delta)
	# iterate all the messages and add every message to its 
	for i in data:
		minutes_groups[i / int(60 * delta)] += 1

	return minutes_groups
	
def parse_time(data):
	# collects the date + hour for every message (including system messages and media)
	full_dates = get_full_dates(data)

	######### dates #########
	dates_dt = get_dates(full_dates)

	weekdays = [0]*7
	months = [0]*12
	for i in dates_dt:
		weekdays[i.weekday() - 1] += 1
		months[i.month - 1] += 1

	######### hours #########
	minutes = get_raw_minutes(full_dates)

	# create the title for every half an hour (e.g. "10:30")
	minutes_groups_titles = [
		"%02d" % (i / 2)
		 +
		(":30" if i % 2 else ":00")
		for i in range(48)
	]

	# create a list of 48 counters for each half an hour
	minutes_groups = get_minutes(minutes)

	hours = zip(minutes_groups_titles, minutes_groups)

	return weekdays, months, hours

###### PLOTTING ######
def plot_weekdays(data=None, width=1/1.5, start=None, end=None):
	data = get_weekdays(data, start, end)

	plt.bar(range(len(data)), data, width, color="blue")
	plt.xticks(range(len(data)), DAYS)
	plt.show()

def plot_months(data=None, width=1/1.5, start=None, end=None):
	data = get_months(data, start, end)

	plt.bar(range(len(data)), data, width, color="blue")
	plt.xticks(range(len(data)), MONTHS)
	plt.show()

def plot_hours(data=None, width=1/1.5, delta=0.5):
	if not data:
		data = get_minutes(delta=delta)
	if delta not in SUPPORTED_HOURS_DELTA:
		raise Exception("Unsupported hour delta")
	
	plt.bar(range(len(data)), data, width, color="blue")
	
	if delta == 0.5:
		minutes_groups_titles = [
			"%02d" % (i / 2)
			 +
			(":30" if i % 2 else ":00")
			for i in range(48)
		]
	elif type(delta) is int:
		minutes_groups_titles = [
			"%02d:00" % (i * delta)
			for i in range(24 / delta)
		]
	plt.xticks(range(len(data)), minutes_groups_titles)
	plt.show()

if __name__ == '__main__':
	import sys
	if sys.argv[1] == '1':
		plot_weekdays()
	elif sys.argv[1] == '2':
		plot_months()
	elif sys.argv[1] == '3':
		plot_hours()
	elif sys.argv[1] == '4':
		plot_hours(delta=1)
	elif sys.argv[1] == '5':
		plot_hours(delta=2)
	elif sys.argv[1] == '6':
		print(len(get_full_dates()))
	elif sys.argv[1] == '7':
		plot_weekdays(start=datetime(2016,1,1))
