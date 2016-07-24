import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.image import BboxImage,imread
from matplotlib.transforms import Bbox

WIDTH = 1/1.5

def _rl(a):
	return range(len(a))

EMOJI_FOLDER = os.path.expanduser("~/Projects/Whatsapp/emoji/images")

LABEL_Y_POS = -.5

ticks = list(range(5))
ticks = [0,2,4,6,8]

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

# set ticks where your images will be
f.get_xaxis().set_ticks(
	[1,2,3,4,5]
)
# remove tick labels
f.get_xaxis().set_ticklabels([])


# add a series of patches to serve as tick labels
f.add_patch(patches.Circle((2,LABEL_Y_POS),radius=.2,
                            fill=True,clip_on=False))
f.add_patch(patches.Circle((4,LABEL_Y_POS),radius=.2,
                            fill=False,clip_on=False))
f.add_patch(patches.Rectangle((6-.1,LABEL_Y_POS-.05),.2,.2,
                               fill=True,clip_on=False))
f.add_patch(patches.Rectangle((8-.1,LABEL_Y_POS-.05),.2,.2,
                               fill=False,clip_on=False))


# for i in ticks[:1]:
# 	lower = f.transData.transform((
# 		( i + 1 )   - .225,
# 		LABEL_Y_POS - .225
# 	))
# 	upper = f.transData.transform((
# 		( i + 1 )   + .225,
# 		LABEL_Y_POS + .225
# 	))
# 	bbox_image = BboxImage(
# 		Bbox(
# 			[
# 				[
# 					lower[0],
# 					lower[1]
# 				],
# 				[
# 					upper[0],
# 					upper[1]
# 				]
# 			]
# 		),
# 		norm    = None,
# 		origin  = None,
# 		clip_on = False,
# 	)
# 	bbox_image.set_data(
# 		imread(
# 			"emoji/images/%s.png" % names[i]
# 		)
# 	)
# 	f.add_artist(bbox_image)
# 	print("emoji/images/%s.png" % names[i])


lowerCorner = f.transData.transform((.8,LABEL_Y_POS-.225))
upperCorner = f.transData.transform((1.2,LABEL_Y_POS+.225))

bbox_image = BboxImage(Bbox([[lowerCorner[0],
                             lowerCorner[1]],
                             [upperCorner[0],
                             upperCorner[1]],
                             ]),
                       norm = None,
                       origin=None,
                       clip_on=False,
                       )

bbox_image.set_data(imread('emoji/images/1f602.png'))
f.add_artist(bbox_image)


# f.xticks(_rl(data), names)
plt.title("emojis!!!")

plt.show()
