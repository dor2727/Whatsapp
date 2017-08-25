#!/usr/bin/env python3
import re
import matplotlib.pyplot as plt
from dateutil.parser import parse as dateutil_parse_date
from datetime import datetime

class Data(object):
	DATE = 0
	TIME = 1

	DAYS   = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
	MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

	SUPPORTED_HOURS_DELTA = [0.5, 1, 2]

	WIDTH = 1/1.5

	def __init__(self, file_path="data/w"):
		self._raw_data = open(file_path, "rb").read()
		self._parse_data()

	def _parse_data(self):
		self.data = [
			[
				# convert dd/mm/yy to datetime
				dateutil_parse_date(i[self.DATE]),
				# convert hh:mm to minutes (02:15 -> 135)
				int(i[self.TIME][:2]) * 60 + int(i[self.TIME][-2:])
			]
			for i in
			re.findall(b"(\d{1,2}/\d{1,2}/\d\d), (\d\d:\d\d) - ", self._raw_data)
		]

	@property
	def dates(self):
		return [i[self.DATE] for i in self.data]
	@property
	def times(self):
		return [i[self.TIME] for i in self.data]

	def filter_dates(self, start=None, end=None):
		if start and end:       func = lambda i: start <= i[self.DATE] < end
		elif start and not end: func = lambda i: start <= i[self.DATE]
		elif not start and end: func = lambda i:          i[self.DATE] < end
		else:                   func = lambda i:          i[self.DATE]

		return filter(func, self.data)


	def get_weekdays(self, start=None, end=None):
		weekdays = [0]*7
		for i in self.filter_dates(start, end):
			weekdays[i[self.DATE].weekday() - 1] += 1
		return weekdays

	def get_months(self, start=None, end=None):
		months = [0]*12
		for i in self.filter_dates(start, end):
			months[i[self.DATE].month - 1] += 1
		return months

	def get_minutes(self, delta=0.5):
		if delta not in self.SUPPORTED_HOURS_DELTA:
			raise Exception("Unsupported hour delta")

		# create a list of 48 counters for each half an hour
		minutes_groups = [0] * int(24. / delta)
		# iterate all the messages and add every message to its
		for i in self.data:
			minutes_groups[int( i[self.TIME] / int(60 * delta) )] += 1

		return minutes_groups

	def get_minutes_title(self, delta=0.5):
		if delta == .5:
			return [
				"%02d" % (i / 2)
				 +
				(":30" if i % 2 else ":00")
				for i in range(48)
			]
		elif delta == int(delta):
			return [
				"%02d:00" % (i * delta)
				for i in range(int(24 / delta))
			]
	

	###### PLOTTING ######
	def plot_weekdays(self, start=None, end=None):
		data = self.get_weekdays(start, end)

		plt.bar(   range(7), data, self.WIDTH, color="blue")
		plt.xticks(range(7), self.DAYS)
		plt.show()

	def plot_months(self, start=None, end=None):
		data = self.get_months(start, end)

		plt.bar(   range(12), data, self.WIDTH, color="blue")
		plt.xticks(range(12), self.MONTHS)
		plt.show()

	def plot_hours(self, delta=0.5):
		if delta not in self.SUPPORTED_HOURS_DELTA:
			raise Exception("Unsupported hour delta")

		plt.bar(   range(int(24 / delta)), self.get_minutes      (delta=delta), self.WIDTH, color="blue")
		plt.xticks(range(int(24 / delta)), self.get_minutes_title(delta=delta))
		plt.show()

if __name__ == '__main__':
	import sys
	command = sys.argv[1]
	d = Data()
	if   command == '1' or command == "weekday": d.plot_weekdays()
	elif command == '2' or command == "month"  : d.plot_months()
	elif command == '3' or command == "hour"   : d.plot_hours()
	elif command == '4' or command == "hour1"  : d.plot_hours(delta=1)
	elif command == '5' or command == "hour2"  : d.plot_hours(delta=2)
	elif command == '6' or command == "len"    : print(len(d.data))
	elif command == '7' or command == "filter" : d.plot_weekdays(start=datetime(2016,1,1))
