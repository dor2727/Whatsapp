import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.image import BboxImage,imread
from matplotlib.transforms import Bbox

WIDTH = 1/1.5

def _rl(a):
	return range(len(a))

EMOJI_FOLDER = os.path.expanduser("~/Projects/Whatsapp/emoji/images")

LABEL_Y_POS = -.6

# add a plot, total of 1X1 plots, this is the #1 plot
f = plt.figure().add_subplot(1,1,1)
d = [['1f603', 120],
	 ['1f62c', 120],
	 ['1f601', 136],
	 ['1f602', 271],
	 ['1f621', 423]]

data = [i[1] for i in d]
names = [i[0] for i in d]

f.bar(_rl(data), data, WIDTH, color="blue")

f.get_xaxis().set_ticks(range(1,1+len(data)))



# f.xticks(_rl(data), names)
# f.title("emojis!!!")

plt.show()
