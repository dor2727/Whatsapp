import os
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from utils.emoji import EMOJI_FOLDER
from utils.other import counter

WIDTH = 1/1.5

##### utils #####

def _rl(a):
	return range(len(a))

##### general #####

def pie(data, labels=None, title=None, legend=True, legend_title=None, axis="equal", **kwargs):
	if labels:
		plt.pie(data, labels=labels)
	else:
		plt.pie(data)

	if title:
		plt.title(title)


	if legend:
		if legend_title:
			plt.legend(title=legend_title)
		else:
			plt.legend()
			
	if axis:
		plt.axis(axis)	

	plt.show()

def bar(data, names=None, color="blue", title=None, axis=None, show=True):
	# create a bar 
	plt.bar(_rl(data), data, WIDTH, color=color)

	# sending an empty list (which erases the xticks) is allowed
	if names is not None:
		# plt.xticks(_rl(data) + WIDTH*0.5, names)
		plt.xticks(_rl(data), names)

	if title:
		plt.title(title)

	if axis:
		if type(axis) is list:
			plt.axis(axis)
		if type(axis) is type(lambda x:x):
			plt.axis(axis(plt.axis()))

	# mpl.rc('font', family='Arial')
	# mpl.rc('font', **{
	# 	'sans-serif' : 'Arial',
	# 	'family' : 'sans-serif'
	# })

	if show:
		plt.show()

def bar_2(data, names=[None, None], color=["blue", "red"], title=["left", "right"], axis=None):
	plt.subplot(1,2,1) # rows, columns, plot number
	bar(
		data=data[0],
		names=names[0],
		color=color[0],
		title=title[0],
		axis=axis,
		show=False
	)
	plt.subplot(1,2,2) # rows, columns, plot number
	bar(
		data=data[1],
		names=names[1],
		color=color[1],
		title=title[1],
		axis=axis,
		show=True
	)

def hist(data, **kwargs):
	# data should be a list
	# create a dict of how many times each object appears
	if type(data) is not list:
		return(bool(print("data should be a list!")))
	if type(data[0]) is list or type(data[0]) is tuple:
		c = data
	elif "__iter__" in dir(data[0]) and type(data[0]) is not str:
		c = [list(i) for i in data]
	else:
		c = counter(data)

	if "sort" in kwargs:
		if kwargs["sort"].lower() == "counter":
			c.sort(key=lambda x: x[1])
		else:
			c.sort(key=kwargs["sort"])
		kwargs.pop("sort")

	if "amount" in kwargs:
		c = c[-kwargs["amount"]:]
		kwargs.pop("amount")

	if "map" in kwargs:
		c = list(map(kwargs["map"], c))
		kwargs.pop("map")

	return bar([i[1] for i in c], names=[i[0] for i in c], **kwargs)

def hist_2(data, color=["blue", "red"], title=["left", "right"], **kwargs):
	# data needs to be a list of (emoji_unicode_id, amount)

	if "sort" in kwargs:
		if kwargs["sort"].lower() == "counter":
			data[0].sort(key=lambda x: x[1])
			data[1].sort(key=lambda x: x[1])
		else:
			data[0].sort(key=kwargs["sort"])
			data[1].sort(key=kwargs["sort"])
		kwargs.pop("sort")

	if "amount" in kwargs:
		data[0] = data[0][-kwargs["amount"]:]
		data[1] = data[1][-kwargs["amount"]:]
		kwargs.pop("amount")

	if "map" in kwargs:
		data[0] = list(map(kwargs["map"], data[0]))
		data[1] = list(map(kwargs["map"], data[1]))
		kwargs.pop("map")

	# data_names is used to display the emojis, it can be joined
	data_names  = [i[0] for i in data[0]] + [i[0] for i in data[1]]
	# data_amount is used to display the bar graph for each user
	data_amount = [
		[i[1] for i in data[0]],
		[i[1] for i in data[1]]
	]
	columns = len(data[0]) + len(data[1])

	bar(
		data=data_amount[0] + [0]*len(data_amount[1]),
		names=data_names,
		color=color[0],
		
		show=False
	)
	
	bar(
		data=[0]*len(data_amount[0]) + data_amount[1],
		names=data_names,
		color=color[1],
		title=" - ".join(title),
		show=True
	)


##### emoji #####

MAX_EMOJI_AMOUNT = 10
def _fit_axis(x):
	return [
		x[0], # x-min
		x[1] - (1-WIDTH), # x-max
		# each bar-column gets '1' size, and its width is WIDTH. Thus, there is a (1-WIDTH) margin left at the end
		x[2], # y-min
		x[3]  # y-max
	]
def emoji_bar(data, **kwargs):
	# data needs to be a list of (emoji_unicode_id, amount)

	if "sort" in kwargs:
		if type(kwargs["sort"]) is str \
			and kwargs["sort"].lower() == "counter":
			data.sort(key=lambda x: x[1])
		else:
			data.sort(key=kwargs["sort"])
		kwargs.pop("sort")

	if "amount" in kwargs:
		data = data[-kwargs["amount"]:]
		kwargs.pop("amount")

	if "map" in kwargs:
		data = list(map(kwargs["map"], data))
		kwargs.pop("map")

	if len(data) > MAX_EMOJI_AMOUNT:
		return(bool(print("len(data) is bigger than MAX_EMOJI_AMOUNT (%s)" % MAX_EMOJI_AMOUNT)))

	if "emoji_path" in kwargs:
		EMOJI_PATH = kwargs["emoji_path"]
		kwargs.pop("emoji_path")
	else:
		EMOJI_PATH = EMOJI_FOLDER + "/%s.png"

	data_names  = [i[0] for i in data]
	data_amount = [i[1] for i in data]
	columns     = len(data)

	# safety
	if not all(map(lambda x: os.path.exists(EMOJI_PATH % x), data_names)):
		return(bool(print("Invalid emoji unicode-id given!")))

	# plot emojis
	for i in range(len(data)):
		# read the image of the emoji
		img = mpimg.imread(EMOJI_PATH % data_names[i])
		plt.subplot(
			MAX_EMOJI_AMOUNT, # amount of rows
			columns, # amount of columns
			1 + ( columns * (MAX_EMOJI_AMOUNT-1) ) + i # plot number
			# 1 based + all the rows except the last one + the index in the last row
		)
		plt.imshow(img)
		plt.axis("off")

	# plot the bar graph
	# focus on all the columns and on all the rows but the last one
	plt.subplot(MAX_EMOJI_AMOUNT,1,(1,MAX_EMOJI_AMOUNT-1))

	return bar(
		data=data_amount,
		names=[], # remove the x-axis labels
		title="EMOJI!!!",
		axis=_fit_axis
	)

def emoji_bar_2(data, color=["blue", "red"], title=["left", "right"], **kwargs):
	# data needs to be a list of (emoji_unicode_id, amount)

	if "sort" in kwargs:
		if type(kwargs["sort"]) is str \
			and kwargs["sort"].lower() == "counter":
			data[0].sort(key=lambda x: x[1])
			data[1].sort(key=lambda x: x[1])
		else:
			data[0].sort(key=kwargs["sort"])
			data[1].sort(key=kwargs["sort"])
		kwargs.pop("sort")

	if "amount" in kwargs:
		data[0] = data[0][-kwargs["amount"]:]
		data[1] = data[1][-kwargs["amount"]:]
		kwargs.pop("amount")

	if "map" in kwargs:
		data[0] = list(map(kwargs["map"], data[0]))
		data[1] = list(map(kwargs["map"], data[1]))
		kwargs.pop("map")

	if len(data[0]) + len(data[1]) > MAX_EMOJI_AMOUNT:
		return(bool(print("len(data[0+1]) is bigger than MAX_EMOJI_AMOUNT (%s)" % MAX_EMOJI_AMOUNT)))

	if "emoji_path" in kwargs:
		EMOJI_PATH = kwargs["emoji_path"]
		kwargs.pop("emoji_path")
	else:
		EMOJI_PATH = EMOJI_FOLDER + "/%s.png"

	# data_names is used to display the emojis, it can be joined
	data_names  = [i[0] for i in data[0]] + [i[0] for i in data[1]]
	# data_amount is used to display the bar graph for each user
	data_amount = [
		[i[1] for i in data[0]],
		[i[1] for i in data[1]]
	]
	columns = len(data[0]) + len(data[1])

	# safety
	if not all(map(lambda x: os.path.exists(EMOJI_PATH % x), data_names)):
		return(bool(print("Invalid emoji unicode-id given!")))

	# plot emojis
	for i in range(columns):
		# read the image of the emoji
		img = mpimg.imread(EMOJI_PATH % data_names[i])
		plt.subplot(
			MAX_EMOJI_AMOUNT, # amount of rows
			columns, # amount of columns
			1 + ( columns * (MAX_EMOJI_AMOUNT-1) ) + i # plot number
			# 1 based + all the rows except the last one + the index in the last row
		)
		plt.imshow(img)
		plt.axis("off")

	# plot the bar graph
	plt.subplot(MAX_EMOJI_AMOUNT,1,(1,MAX_EMOJI_AMOUNT-1))

	bar(
		data=data_amount[0] + [0]*len(data_amount[1]),
		names=[], # remove the x-axis labels
		color=color[0],
		
		show=False
	)
	
	bar(
		data=[0]*len(data_amount[0]) + data_amount[1],
		names=[], # remove the x-axis labels
		color=color[1],
		title=" - ".join(title),
		show=True
	)

##### dates #####

SUPPORTED_HOURS_DELTA = [0.5, 1, 2]
DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def _filter_dates(data, start, end):
	"data = wp.d.lines"
	if "__iter__" in dir(data[0]):
		data = map(lambda x:x[0], data)

	if start and end:
		return [i for i in data if start <= i < end]
	elif start and not end:
		return [i for i in data if start <= i      ]
	elif not start and end:
		return [i for i in data if          i < end]
	else:
		return [i for i in data if          i      ]

def hours(data, delta=0.5, start=None, end=None):
	"data = wp.d.lines"
	if delta not in SUPPORTED_HOURS_DELTA:
		return(bool(print("Unsupported hour delta")))

	# create a list of all the hours with apropriate delta
	minutes_groups = [0] * int(24. / delta)

	for i in _filter_dates(data, start, end):
		minutes_groups[
			(i.minute + i.hour * 60)
			 //
			int(60 * delta)
		] += 1

	if delta == 0.5:
		# minutes_groups_titles = [
		# 	"%02d" % (i // 2)
		# 	 +
		# 	(":30" if i % 2 else ":00")
		# 	for i in range(48)
		# ]
		minutes_groups_titles = [
			(
				'.5'
				 if
				i % 2
				 else
				"%02d" % (i * delta)
			)
			for i in range(48)
		]
	elif delta == int(delta):
		minutes_groups_titles = [
			"%02d:00" % (i * delta)
			for i in range(24 // delta)
		]

	return bar(minutes_groups, minutes_groups_titles, title="Hours")

def days(data, start=None, end=None):
	"data = wp.d.lines"
	weekday = [0]*7
	for i in _filter_dates(data, start, end):
		weekday[i.weekday()] += 1

	return bar(weekday, DAYS, title="Weekdays")

def months(data, start=None, end=None):
	"data = wp.d.lines"
	months = [0]*12
	for i in _filter_dates(data, start, end):
		months[i.month - 1] += 1

	return bar(months, MONTHS, title="Months")
