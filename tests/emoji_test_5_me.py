import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.image import BboxImage,imread
from matplotlib.transforms import Bbox

WIDTH = 1/1.5

def _rl(a):
	return range(1,1+len(a))

EMOJI_FOLDER = os.path.expanduser("~/Projects/Whatsapp/emoji/images")

# add a plot, total of 1X1 plots, this is the #1 plot
f = plt.figure().add_subplot(1,1,1)
d = [['1f603', 120],
	 ['1f62c', 120],
	 ['1f601', 136],
	 ['1f602', 271],
	 ['1f621', 423]]
d = d[::-1]
d.append([" ",0]) # PlaceHolder
data  = [i[1] for i in d]
names = [i[0] for i in d]

plt.bar(_rl(data), data, WIDTH, color="blue")

plt.xticks(list(map(lambda x: x+WIDTH*0.5,_rl(data))), names)
# plt.xticks(_rl(data), names)

plt.title("emojis!!!")

plt.show()



# # for i in ticks[:1]:
# # 	lower = f.transData.transform((
# # 		( i + 1 )   - .225,
# # 		LABEL_Y_POS - .225
# # 	))
# # 	upper = f.transData.transform((
# # 		( i + 1 )   + .225,
# # 		LABEL_Y_POS + .225
# # 	))
# # 	bbox_image = BboxImage(
# # 		Bbox(
# # 			[
# # 				[
# # 					lower[0],
# # 					lower[1]
# # 				],
# # 				[
# # 					upper[0],
# # 					upper[1]
# # 				]
# # 			]
# # 		),
# # 		norm    = None,
# # 		origin  = None,
# # 		clip_on = False,
# # 	)
# # 	bbox_image.set_data(
# # 		imread(
# # 			"emoji/images/%s.png" % names[i]
# # 		)
# # 	)
# # 	f.add_artist(bbox_image)
# # 	print("emoji/images/%s.png" % names[i])
