import enum
from utils.re import escape as _escape
from utils.enum import enum_getter

# emoticons taken from
# https://en.wikipedia.org/wiki/List_of_emoticons


SWAPPABLE = {
	'('  : ')' ,
	')'  : '(' ,
	'['  : ']' ,
	']'  : '[' ,
	'{'  : '}' ,
	'}'  : '{' ,
	'<'  : '>' ,
	'>'  : '<' ,
	'/'  : '\\',
	'\\' : '/' ,
	'b'  : 'd' ,
	'd'  : 'b' ,
}

def _reverse_emoticon(x):
	return ''.join(SWAPPABLE.get(i, i) for i in x[::-1])
	
def _format_emoticon(x, nose=False, reverse=False):
	res = [x]
	if nose:
		res.append(x[:-1] + '-' + x[-1])
	if reverse:
		res.append(         _reverse_emoticon(x) )
	if nose and reverse:
		r = _reverse_emoticon(x)
		res.append(r[0] + '-' + r[1:])
	return res
_fe = _format_emoticon

class EMOTICON_TYPE(enum.Enum):
	HAPPY = [
		*_fe( ":)"  , 1, 1 ),
		*_fe( ":')" , 1, 1 ),
		*_fe( ":]"  , 1, 1 ),
		*_fe( ":>"  , 1, 1 ),
		*_fe( ":}"  , 1, 1 ),
		# this returns the number 8 and the end of brackets
		# *_fe( "8)"  , 1, 1 ),
		# this returns hours "10:30"
		# *_fe( ":3"  , 1, 0 ),
		*_fe( ":^)" , 0, 1 ),
		*_fe( "=)"  , 0, 1 ),
		*_fe( "=]"  , 0, 1 ),
		*_fe( ":o)" , 0, 0 ),
		*_fe( ":c)" , 0, 0 ),
	]
	LAUGH = [
		*_fe( ":D"  , 1, 0 ),
		*_fe( "8D"  , 1, 0 ),
		*_fe( "xD"  , 1, 0 ),
		*_fe( "XD"  , 1, 0 ),
		# these retrun http parameters
		# *_fe( "=D"  , 0, 0 ),
		# *_fe( "=3"  , 0, 0 ),
		*_fe( "B^D" , 0, 0 ),
		*_fe( "lol" , 0, 0 ),
	]
	SAD = [
		*_fe( ":("  , 1, 1 ),
		*_fe( ":'(" , 1, 1 ),
		*_fe( ":`(" , 1, 1 ),
		*_fe( ":<"  , 1, 1 ),
		*_fe( ":["  , 1, 1 ),
		*_fe( ":{"  , 1, 1 ),
	]
	ANGRY = [
		*_fe( ">:[" , 0, 1 ),
		*_fe( ">:(" , 0, 1 ),
		*_fe( ":@"  , 0, 0 ),
	]
	HORROR = [
		*_fe( "D-':", 0, 0 ),
		*_fe( "D:<" , 0, 0 ),
		*_fe( "D:"  , 0, 0 ),
		*_fe( "D8"  , 0, 0 ),
		*_fe( "D;"  , 0, 0 ),
		*_fe( "D="  , 0, 0 ),
		*_fe( "DX"  , 0, 0 ),
	]
	SUPRISE = [
		*_fe( ":O"  , 1, 1 ),
		*_fe( ":o"  , 1, 1 ),
		*_fe( ":-0" , 0, 1 ),
		*_fe( "8-0" , 0, 1 ),
		*_fe( ">:O" , 0, 0 ),
	]
	KISS = [
		*_fe( ":*"  , 1, 1 ),
		*_fe( ":x"  , 0, 1 ),
	]
	WINK = [
		*_fe( "*)"  , 1, 1 ),
		*_fe( ";)"  , 1, 0 ),
		*_fe( ";]"  , 1, 0 ),
		# this returs "TL;DR"
		# *_fe( ";D"  , 0, 0 ),
		*_fe( ";^)" , 0, 0 ),
		*_fe( ":-," , 0, 0 ),
	]
	TONGUE = [
		*_fe( ":P"  , 1, 0 ),
		*_fe( ":p"  , 1, 0 ),
		*_fe( "XP"  , 1, 0 ),
		*_fe( "Xp"  , 1, 0 ),
		*_fe( ":b"  , 1, 1 ),
		# these retrun http parameters
		# *_fe( "=p"  , 1, 0 ),
		# *_fe( "=P"  , 1, 0 ),
		# *_fe( "=b"  , 1, 1 ),
		*_fe( ">:P" , 1, 0 ),
	]
	CONFUSED = [
		# ":/" has to be the first!
		# I am replacing it with a special regex when creating
		# EMOTICON_REGEX since it matches "http://"
		*_fe( ":/"  , 1, 1 ),
		*_fe( ":|"  , 1, 1 ),
		*_fe( ":\\" , 1, 1 ),
		*_fe( "=/"  , 1, 1 ),
		*_fe( "=\\" , 1, 1 ),
		*_fe( ">:/" , 1, 1 ),
		*_fe( ">:\\", 1, 1 ),
		*_fe( ":L"  , 0, 0 ),
		*_fe( "=L"  , 0, 0 ),
		*_fe( ":-." , 0, 0 ),
		*_fe( ":S"  , 0, 0 ),
		*_fe( "o.O" , 0, 1 ),
		*_fe( "O_o" , 0, 1 ),
		*_fe( "O_O" , 0, 0 ),
		*_fe( "o_o" , 0, 0 ),
		*_fe( "O-O" , 0, 0 ),
		*_fe( "o-o" , 0, 0 ),
	]
	NO_EXPRESSION = [
		*_fe( ":|"  , 0, 1 ),
	]
	LOVE = [
		*_fe( "<3"  , 0, 0 ),
	]
	NOLOVE = [
		*_fe( "</3" , 0, 0 ),
		*_fe( "<\\3", 0, 0 ),
	]
	# OTHER = [	]
ET = enum_getter(EMOTICON_TYPE)

EMOTICON_NAMES = list(EMOTICON_TYPE.__members__.keys())

def _emoticon_type_to_regex(name):
	values = ET(name)
	values = list(map(_escape, values))
	# avoid capturing http://
	# python regex has to use fixed size regex lookbehinds
	# and, apparently, using 2 negative lookbehind works o.O
	if values[0] == ":/":
		values[0] = "(?<!http)(?<!https):/"
	return '(' + '|'.join(values) + ')'

# dynamically create the regex enum
EMOTICON_REGEX = enum.Enum(
	"EMOTICON_REGEX",	# class name
	zip(				# an iterable of (name, value)
		EMOTICON_NAMES,
		map(
			_emoticon_type_to_regex,
			EMOTICON_NAMES
		)
	)
)
ER = enum_getter(EMOTICON_REGEX)

PATTERN = (
	'('
	 + 
	'|'.join(
		map(
			lambda x: x.value[1:-1], # remove the '(' & ')'
			EMOTICON_REGEX
		)
	)
	 + 
	')'
)
PATTERN_HAPPY = (
	'('
	 + 
	'|'.join(
		map(
			lambda x: ER(x)[1:-1], # remove the '(' & ')'
			[
				"HAPPY",
				"LAUGH",
				"KISS",
				"WINK",
				"TONGUE",
				"LOVE",
			]
		)
	)
	 + 
	')'
)
PATTERN_SAD = (
	'('
	 + 
	'|'.join(
		map(
			lambda x: ER(x)[1:-1], # remove the '(' & ')'
			[
				"SAD",
				"ANGRY",
				"NOLOVE",
			]
		)
	)
	 + 
	')'
)

def get_emoticon_type(x, return_str=False):
	a = [i for i in EMOTICON_NAMES if x in ET(i)]
	if len(a) > 1:
		return a[0] if return_str else a
	elif len(a) == 1:
		return a[0]
	else:
		return '' if return_str else None