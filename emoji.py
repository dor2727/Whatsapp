#!/usr/bin/env python3

import os
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

WIDTH = 1/1.5

def _rl(a):
	return range(len(a))

EMOJI_FOLDER = os.path.expanduser("~/Projects/Whatsapp/emoji/images")

EMOJI_PATH = EMOJI_FOLDER + "/%s.png"

d = [['0x1f389', 81],
	 ['0x1f61c', 83],
	 ['0x1f633', 96],
	 ['0x1f44d', 108],
	 ['0x1f605', 112],
	 ['0x1f603', 120],
	 ['0x1f62c', 120],
	 ['0x1f601', 136],
	 ['0x1f602', 271],
	 ['0x1f621', 423]]


data  = [i[1]     for i in d]
names = [i[0][2:] for i in d]
columns = len(data)

# safety
if not all(map(
	lambda x: os.path.exists(EMOJI_PATH % x),
	names
)):
	exit(bool(print("failed parsing emoji")))

plt.subplot(columns,1,(1,columns - 1))

plt.bar(_rl(data), data, WIDTH, color="blue")
plt.title("emojis!!!")
plt.xticks([])
tmp = plt.axis()
tmp2 = [tmp[0], tmp[1]-(1-WIDTH), tmp[2], tmp[3]]
plt.axis(tmp2)

for i in _rl(data):
	img = mpimg.imread(EMOJI_PATH % names[i])
	plt.subplot(
		columns,
		columns,
		( columns * (columns-1) ) + 1 + i
	)
	plt.imshow(img)
	plt.axis("off")

plt.show()
