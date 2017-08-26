import os
import re
import enum
import utils.re
from utils.enum import enum_getter
from collections import Counter

#################################
########## EMOJI DATA  ##########
#################################

EMOJI_FOLDER = os.path.expanduser("~/Projects/Whatsapp/emoji/images")

# depricated
EMOJI_TYPES_DESCRIPTION = """
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
	hand gestures : 
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
		1f3[00 - 2c]
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
	hand gestures : 
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
	hand gestures : 
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
	hand gestures : 
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
	hand gestures : 
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

# enum of MEANING : REGEX
class EMOJI_TYPE(enum.Enum):
	"The type of the emoji is determined by its first char only!"
	academy = "1f39[0-9]"
	accessories = [
		"1f45[a-f]",
		"1f45[1-9]", "1f46[0-3]"
	]
	animals = [
		"1f4[0-3][0-9a-f]",
		"1f98[0-4]"
	]
	arrows = [
		"2b0[5-7]",
		"219[4-9]",
		"293[4-5]",
		"27a1"
	]
	ascii = ["00a9", "00ae"]
	black_white_circles = "26a[a-b]"
	black_white_squares = [
		"2b1[bc]",
		"25a[ab]",
		"25f[b-e]"
	]
	body_parts = "1f44[0-5]"
	cards = "266[0356]"
	clocks = [
		"1f5[56][0-9]",
		"1f570",
		"23f[0-3]",
		"231[a-b]"
	]
	colors = "1f3f[bcdef]"
	families = "1f46[6-9]"
	flags = ["1f1e[6-9a-f]","1f1f[0-9a-f]"]
	food = [
		"1f3[4][5-9a-f]",
		"1f3[5-7][0-9a-f]",
		"1f32[d-f]",
		"1f9c0"
	]
	hand_gestures = [
		"1f44[a-f]",
		"1f44[6-9]", "1f450",
		"1f59[0-6]",
		"261d",
		"270[a-f]"
	]
	hearts = "1f49[2-9]"
	holidays = "1f38[0-9]"
	letters = [
		"1f17[ef]",
		"1f183",
		"1f19a",
		"1f21a",
		"1f22f",
		"1f23a",
		"1f1[7-9][0-9a-f]", # random letters English
		"1f2[0-9a-f][0-9a-f]", # random letters Chinese
	]
	numpad = [
		"003[0-9]", # 0-9
		"0023", # '#'
		"002a"  # '*'
	]
	people = [
		"1f46[4-5a-f]",
		"1f47[0-9a-f]",
		"1f48[0-7]",
		"1f49[0-1]"
	]
	plants = [
		"1f33[0-9a-f]",
		"1f34[0-4]"
	]
	remote_controller = [
		"21a[9a]",
		"21e[9-f]",
		"23e[9a-f]",
		"23f[8-a]",
		"25b6",
		"25c0"
	]
	smiley = [
		"1f6[0-4][0-9a-f]",
		"1f91[0-8]",
		"263a",
		"2620",
		"2639"
	]
	transport = "1f6[8-9][0-9a-f]"
	weather = [
		"1f3[0-2][0-9]",
		"1f3[01][a-f]",
		"1f32[a-c]",
	]

	other = [
		"1f0cf",
		"1f3[a-e][0-9a-f]", "1f3f[0-9a]",
		"1f004",
		"1f[456][a-f][0-9a-f]",
		"1f3[89][a-f]",
		"1f4[89][a-f]",
		"1f48[89]",
		"1f5[0-8][a-f]",
		"1f5[0-4][0-9]",
		"1f57[3-9]",
		"1f587",
		"2b50",
		"2b55",
		"24c2",
		"26a[0-1]",
		"26[b-f][0-f]",
		"27b0",
		"27bf",
		"203c",
		"260e",
		"262[a-f]",
		"264[a-f]",
		"267b",
		"267f",
		"269b",
		"269c",
		"271d",
		"274c",
		"274e",
		"303d",
		"2049",
		"2122",
		"2139",
		"2328",
		"2[6-7][0-9][0-9]",
		"3030",
		"3297",
		"3299"
	]
E = enum_getter(EMOJI_TYPE)

class EMOJI_MEANING(enum.Enum):
	ANGRY = [
		"1f47f",
		"1f595_1f3fb",
		"1f595_1f3fc",
		"1f595_1f3fd",
		"1f595_1f3fe",
		"1f595_1f3ff",
		"1f595",
		"1f608",
		"1f620",
		"1f621",
		"1f624",
	]
	CONFUSED = [
		"1f616",
		"1f623",
	]
	HAPPY = [
		"1f388",
		"1f389",
		"1f600",
		"1f601",
		"1f603",
		"1f604",
		"1f605",
		"1f607",
		"1f60a",
		"1f60c",
		"1f62c",
		"1f638",
		"1f63a",
		"1f642",
		"1f643",
		"263a",
	]
	KISS = [
		"1f48b",
		"1f61a",
		"1f63d",
	]
	LAUGH = [
		"1f602",
		"1f606",
		"1f639",
	]
	LOVE = [
		"1f468_200d_2764_fe0f_200d_1f468",
		"1f468_200d_2764_fe0f_200d_1f48b_200d_1f468",
		"1f469_200d_2764_fe0f_200d_1f468",
		"1f469_200d_2764_fe0f_200d_1f469",
		"1f469_200d_2764_fe0f_200d_1f48b_200d_1f468",
		"1f469_200d_2764_fe0f_200d_1f48b_200d_1f469",
		"1f48c",
		"1f48f",
		"1f491",
		"1f492",
		"1f493",
		"1f495",
		"1f496",
		"1f497",
		"1f498",
		"1f499",
		"1f49a",
		"1f49b",
		"1f49c",
		"1f49d",
		"1f49e",
		"1f49f",
		"1f60d",
		"1f63b",
		"2665",
		"2764",
	]
	NO_EXPRESSION = [
		"1f610",
		"1f611",
		"1f612",
		"1f615",
		"1f634",
		"1f636",
		"1f644",
	]
	NOLOVE = [
		"1f494",
	]
	SAD = [
		"1f613",
		"1f614",
		"1f61e",
		"1f61f",
		"1f622",
		"1f625",
		"1f629",
		"1f62a",
		"1f62b",
		"1f62d",
		"1f63f",
		"1f641",
		"2639",
	]
	SUPRISE = [
		"1f626",
		"1f627",
		"1f628",
		"1f62e",
		"1f62f",
		"1f630",
		"1f631",
		"1f632",
		"1f633",
		"1f635",
		"1f640",
	]
	TONGUE = [
		"1f60b",
		"1f61b",
		"1f61c",
		"1f61d",
	]
	WINK = [
		"1f609",
		"1f60e",
		"1f60f",
	]
EM = enum_getter(EMOJI_MEANING)

EMOJI_MEANING_NAMES = list(EMOJI_MEANING.__members__.keys())

EMOJI_COLORS = ["1f3f"+i for i in "bcdef"]

#################################
##########   HELPERS   ##########
#################################

### general

# improved ord
def emoji_to_hex(x):
	return '_'.join([
		"%04x" % ord(i)
		for i in x
	])
# improved chr
def hex_to_emoji(x):
	return ''.join([
		chr(int(i,0x10))
		for i in x.split('_')
	])

def get_first_char(x):
	if type(x) is str:
		return x.split('_')[0]
	elif type(x) is list:
		first_char = map(
			lambda i: i.split('_')[0],
			x
		)
		return list(first_char)
	else:
		return(bool(print("please enter a string or a list")))

### flags

_FLAG_A = "\U0001f1e6"
_FLAG_Z = "\U0001f1ff"
# _FLAGS_PATTERN = re.compile("[\U0001f1e6-\U0001f1ff]")
_FLAGS_PATTERN = re.compile("[%s-%s]" % (_FLAG_A, _FLAG_Z))
def flag_to_country(x):
	if _FLAGS_PATTERN.match(x):
		return ''.join([
			chr(ord(i) - ord(_FLAG_A) + ord('A'))
			for i in x
			if re.match("[\U0001f1e6-\U0001f1ff]", i)
		])
	elif '_' in x:
		return ''.join([
			chr(int(i,0x10) - ord(_FLAG_A) + ord('A'))
			for i in x.split('_')
			if _to_re(EMOJI_TYPE.flags.value).match(i)
		])
	else:
		return(bool(print("unknown type")))

def country_to_flag(x):
	return '_'.join([
		"%02x" % (ord(i.upper()) - ord('A') + ord(_FLAG_A))
		for i in x
	])

### emoji type

# convert string or '|'.join(list) to ^regex$
def _to_re(x):
	if type(x) is list:
		x = '|'.join(x)
	return re.compile("^(%s)$" % x)

# iterate EMOJI_TYPE and return the name that matches the emoji
def _r(s):
	return map(
		lambda x: x.name,
		filter(
			lambda x: _to_re(x.value).match(s),
			EMOJI_TYPE
		)
	)

# get the type of the emoji
def get_emoji_type(x):
	if type(x) is not str:
		return(bool(print("x has to be a string")))
	
	return list(_r(get_first_char(x)))[0]

def get_emoji_meaning(x, return_str=False):
	a = [i for i in EMOJI_MEANING_NAMES if emoji_to_hex(x) in EM(i)]
	if len(a) > 1:
		return a[0] if return_str else a
	elif len(a) == 1:
		return a[0]
	else:
		return '' if return_str else None

#################################
##########  LS TO RE   ##########
#################################

def _ls(folder):
	# All the files in the folder
	directory_content = os.listdir(folder)
	directory_content = map(
		lambda x: x[:-4],
		directory_content
	)
	directory_content = list(directory_content)
	directory_content.sort()
	return directory_content

def _ls_to_re():
	data = _ls(EMOJI_FOLDER)
	# data is sorted, so 1f3c3 will be before 1f3c3_1f3fb, thus I will not be able to catch it
	# re.findall("a|a1|a2|a3|a4|a5", "hello a4a4a2b4a1b5aa3") --> ['a', 'a', 'a', 'a', 'a', 'a']
	# re.findall("a5|a4|a3|a2|a1|a", "hello a4a4a2b4a1b5aa3") --> ['a4', 'a4', 'a2', 'a1', 'a', 'a3']
	data = data[::-1]
	data = map(
		lambda x: utils.re.escape(hex_to_emoji(x)),
		data
	)
	return '|'.join(data)

PATTERN = _ls_to_re()
PATTERN_HAPPY = re.compile(
	'('
	 + 
	'|'.join(
		map(
			hex_to_emoji,
			(
				EM("HAPPY")
				 + 
				EM("KISS")
				 + 
				EM("LAUGH")
				 + 
				EM("LOVE")
				 + 
				EM("TONGUE")
				 + 
				EM("WINK")
			)
		)
	)
	 + 
	')'
)
PATTERN_SAD = re.compile(
	'('
	 + 
	'|'.join(
		map(
			hex_to_emoji,
			(
				EM("ANGRY")
				 + 
				EM("NOLOVE")
				 + 
				EM("SAD")
			)
		)
	)
	 + 
	')'
)

# def _test_regex():
	# exec(open("tests/ls_to_re.py").read())
	# # import tests.ls_to_re
	# c_emoji = wp.d.get_messages(ls_to_re())
	# c_non_letter = wp.d.get_messages('|'.join(wp.d._get_non_letters()))
	# c_non_letter2 = wp.d.get_messages('|'.join(''.join(map(lambda x:x[2],wp.d.lines))))
	# c_not_in_emoji = [i for i in c_non_letter if i not in c_emoji]
	# c_not_in_non_letter = [i for i in c_emoji if i not in c_non_letter]

	# print("c_emoji :", len(c_emoji))
	# print("c_non_letter :", len(c_non_letter))
	# print("c_not_in_emoji :", len(c_not_in_emoji))
	# print("c_not_in_non_letter :", len(c_not_in_non_letter))

# def test():
	# directory_content = ls("/home/me/Dropbox/Projects/Whatsapp/emoji/images")
	# first_char = get_first_char(directory_content)
	# first_char_unique = list(set(first_char))

	# a = list(zip(directory_content, map(get_emoji_type, get_first_char(directory_content))))
	# def f(x):
	# 	print(x.__repr__())
	# 	return(" - ".join(x))
	# b = list(map(f,a))

	# single_char, multiple_char = single_multiple_char(directory_content)
	# single_char_re, multiple_char_re = single_multiple_char_re(single_char, multiple_char)


def counter(data):
	return [
		[ emoji_to_hex(i[0]), i[1] ]
		for i in Counter(data).items()
	]
