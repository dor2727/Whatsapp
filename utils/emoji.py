import re
import os

def load_all_emojis(path="emoji/images"):
	# get all files
	a = os.listdir(path)
	# remove the ".png"
	b = [i[:-4] for i in a]
	c = map(
		lambda x: ''.join([chr(int(i, 0x10)) for i in x.split('_')]),
		b
	)
	return c

basic_regex = '|'.join(load_all_emojis())