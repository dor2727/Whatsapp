import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.image import BboxImage,imread
from matplotlib.transforms import Bbox

d = [['1f603', 120],
	 ['1f62c', 120],
	 ['1f601', 136],
	 ['1f602', 271],
	 ['1f621', 423]]

data = [i[1] for i in d]
names = [i[0] for i in d]


WIDTH = 1/1.5

def _rl(a):
	return range(len(a))


# define where to put symbols vertically
TICKYPOS = -.5

fig = plt.figure()
ax = fig.add_subplot(111)
# ax.plot(range(10))
ax.bar(_rl(data), data, WIDTH, color="blue")

# set ticks where your images will be
ax.get_xaxis().set_ticks([2,4,6,8])
# ax.get_xaxis().set_ticks([0,1,2,3,4,5,6,7,8,9])
# remove tick labels
# ax.get_xaxis().set_ticklabels([])


# add a series of patches to serve as tick labels
ax.add_patch(patches.Circle((2,TICKYPOS),radius=.2,
														fill=True,clip_on=False))
ax.add_patch(patches.Circle((4,TICKYPOS),radius=.2,
														fill=False,clip_on=False))
ax.add_patch(patches.Rectangle((6-.1,TICKYPOS-.05),.2,.2,
															 fill=True,clip_on=False))
ax.add_patch(patches.Rectangle((8-.1,TICKYPOS-.05),.2,.2,
															 fill=False,clip_on=False))

ticks = [0,2,4,6,8]

a = []

for i in ticks[:2]:
	lowerCorner = ax.transData.transform(((i+1-.225),TICKYPOS-.225))
	# lowerCorner = ax.transData.transform((0.775,TICKYPOS-.225))
	upperCorner = ax.transData.transform(((i+1+.225),TICKYPOS+.225))
	# upperCorner = ax.transData.transform((1.225,TICKYPOS+.225))

	bbox_image = BboxImage(Bbox([[lowerCorner[0],
								 lowerCorner[1]],
								 [upperCorner[0],
								 upperCorner[1]],
								 ]),
								 norm = None,
								 origin=None,
								 clip_on=False,
								 )

	bbox_image.set_data(imread('emoji/images/%s.png' % names[i]))
	a.append(bbox_image)
	ax.add_artist(bbox_image)

plt.xticks(_rl(a), a)

plt.show()