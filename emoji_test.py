import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.image import BboxImage,imread
from matplotlib.transforms import Bbox

# define where to put symbols vertically
TICKYPOS = -.6

fig = plt.figure()
ax = fig.add_subplot(111)
ax.plot(range(10))

# set ticks where your images will be
ax.get_xaxis().set_ticks([2,4,6,8])
# remove tick labels
ax.get_xaxis().set_ticklabels([])


# add a series of patches to serve as tick labels
ax.add_patch(patches.Circle((2,TICKYPOS),radius=.2,
                            fill=True,clip_on=False))
ax.add_patch(patches.Circle((4,TICKYPOS),radius=.2,
                            fill=False,clip_on=False))
ax.add_patch(patches.Rectangle((6-.1,TICKYPOS-.05),.2,.2,
                               fill=True,clip_on=False))
ax.add_patch(patches.Rectangle((8-.1,TICKYPOS-.05),.2,.2,
                               fill=False,clip_on=False))

lowerCorner = ax.transData.transform((.8,TICKYPOS-.225))
upperCorner = ax.transData.transform((1.2,TICKYPOS+.225))

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
ax.add_artist(bbox_image)

plt.show()