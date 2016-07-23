import matplotlib as mpl
import matplotlib.pyplot as plt

from collections import Counter

WIDTH = 1/1.5

def _rl(a):
	return range(len(a))

def hist(data, **kwargs):
	# data should be a list
	# create a dict of how many times each object appears
	if type(data) is not list:
		return(bool(print("data should be a list!")))
	if type(data[0]) is list or type(data[0]) is tuple:
		c = data
	else:
		c = list(Counter(data).items())

	if "sort" in kwargs:
		c.sort(key=kwargs["sort"])
		kwargs.pop("sort")

	if "amount" in kwargs:
		c = c[-kwargs["amount"]:]
		kwargs.pop("amount")

	if "map" in kwargs:
		c = list(map(kwargs["map"], c))
		kwargs.pop("map")

	bar([i[1] for i in c], names=[i[0] for i in c], **kwargs)

def pie(data, labels=None, legend=True, legend_title=None, axis="equal", **kwargs):
	if labels:
		plt.pie(data, labels=labels)
	else:
		plt.pie(data)

	if legend:
		if legend_title:
			plt.legend(title=legend_title)
		else:
			plt.legend()
			
	if axis:
		plt.axis(axis)	

	plt.show()

def bar(data, names=None, color="blue", title=None):
	# create a bar 
	plt.bar(_rl(data), data, WIDTH, color=color)

	if names:
		# plt.xticks(_rl(data) + WIDTH*0.5, names)
		plt.xticks(_rl(data), names)

	if title:
		plt.title(title)

	# mpl.rc('font', family='Arial')
	# mpl.rc('font', **{
	# 	'sans-serif' : 'Arial',
	# 	'family' : 'sans-serif'
	# })

	plt.show()

