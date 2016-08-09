#!/usr/bin/env python3
import re
import os
import sys
import matplotlib as mat
import numpy as np
import scipy as sp

"""
	other : 
		1f0cf
	ascii : 
		00a9 - ©
		00ae - ®
	flags : 
		1f1[e6 - ff] _ 1f1[e6 - ff]
	other : 
		1f3[a0 - fa]
	colors : 
		1f3f[bcdef]
	other : 
		1f004
	other : 
		1f[456][a0 - ff] # many missing parts
	random letters : 
		1f17[ef]
		1f183
		1f19a
		1f21a
		1f22f
		1f23a
	food : 
		1f3[0-7][a-f]
	other : 
		1f3[89][a-f]
	animals : 
		1f4[0-3][a-f]
	hand guestures : 
		1f44[a-f]
	accessories : 
		1f45[a-f]
	people : 
		1f4[6-7][a-f]
	other : 
		1f[48 - 58][a-f]
	emojis : 
		1f6[0-4][a-f]
	transport : 
		1f6[8-9][a-f]
	random letters English : 
		1f1[70 - 99] # many missing parts
	random letters Chinese : 
		1f2[01 - 51] # many missing parts
		# 1f2[0-f][0-f]
	weather : 
		1f3[0-2][0-9]
	plants + food : 
		1f3[3-7][0-9]
	holidays : 
		1f38[0-9]
	academy : 
		1f39[0-9]
	animals : 
		1f4[0-3][0-9]
	body parts : 
		1f44[0-5]
	hand guestures : 
		1f4[46 - 50] # 0-9
	accessories : 
		1f4[51 - 63] # 0-9
	people : 
		1f4[64 - 91] # 0-9
		# 1f46[89]* are families : 
			1f466 - son
			1f467 - dauther
			1f468 - father
			1f469 - mother
			200d - "plus"
			2764 - heart
			fe0f - idk.. maybe changes the heart to pink
	hearts : 
		1f49[2-9]
	other : 
		1f5[0-4][0-9]
	clock : 
		1f5[50 - 70] # 0-9
	other : 
		1f57[3-9]
		1f587
	hand guestures : 
		1f59[0-6]
	emojis : 
		1f6[0-4][0-9]
	transport : 
		1f6[8-9][0-9]
	emojis : 
		1f91[0-8]
	animals : 
		1f98[0-4]
	black & white squares : 
		2b1[bc]
	arrows : 
		2b0[5-7]
	other : 
		2b50
		2b55
	remote controller : 
		21a[9a]
		21e[9-f]
	clocks : 
		23f[0-3]
	remote controller : 
		23f[8-a]
	other : 
		24c2
	black & white squares : 
		25f[b-e]
	other : 
		26a[0-1]
	black & white circles : 
		26a[a-b]
	other : 
		26[b-f][0-f]
		27b0
		27bf
	numbers : 
		003[0-9]_f30f_20e3
		0023_f30f_20e3 # '#'
		002a_f30f_20e3 # '*'
	other : 
		203c
	clocks : 
		231[a-b]
	other : 
		260e
	hand guestures : 
		261d
	other : 
		262[a-f]
	emojis : 
		263a
	other : 
		264[a-f]
		267b
		267f
		269b
		269c
	hand guestures : 
		270[a-f]
	other : 
		271d
		274c
		274e
		303d
		2049
		2122
		2139
	arrows : 
		219[4-9]
	other : 
		2328
		26[0-5][0-9]
	emojis : 
		2620
		2639
	cards : 
		266[0356]
	other : 
		2[6-7][0-9][0-9] # lots of missing parts
	arrows : 
		293[4-5]
	other : 
		3030
		3297
		3299
"""

EMOJI_COLORS = ["1f3f"+i for i in "bcdef"]

# All the files in the folder
directory_content = os.listdir("/home/me/Dropbox/Projects/Whatsapp/emoji/images")
directory_content = map(
	lambda x: x[:-4],
	directory_content
)
directory_content = list(directory_content)
directory_content.sort()

# Only the first char of all the emojis
first_char = map(
	lambda x: x.split('_')[0],
	directory_content
)
first_char = list(first_char)
first_char_unique = list(set(first_char))

# All the emojis that have only one char
one_char = filter(
	lambda x: '_' not in x,
	directory_content
)
one_char = list(one_char)

# Identifying the initial char into 2 groups - 
#     a one-char emoji, that has no variations
#     multi-char emojis, that may have a one-char variation
single_char   = filter(
	lambda x: 
		# A one-char emoji
		x in one_char
		 and
		# That has no variations
		first_char.count(x) == 1
		 and
		x not in EMOJI_COLORS,
	directory_content
)
single_char = list(single_char)


multiple_char = filter(
	lambda x: 
		# Multiple-char emoji
		x not in one_char
		 or
		# A one-char emoji, that has variations
		first_char.count(x) > 1,
	directory_content
)
multiple_char = filter(
	lambda x: "200d" not in x,
	multiple_char
)
multiple_char = list(multiple_char)
multiple_char_first = map(
	lambda x: x.split('_')[0],
	multiple_char
)
multiple_char_first = list(set(multiple_char_first))

# REGEX
re_single_char   = '|'.join([chr(int(i,0x10)) for i in single_char])
re_multiple_char = '|'.join([
	''.join([
		chr(int(j,0x10))
		for j in i.split('_')
	]).replace('*', '\\*')
	for i in multiple_char
])

# exclude "200d"
# exclude 1f3f[bcdef]