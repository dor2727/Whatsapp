# it's ok to import re in a module named re sinced this module will be called though
# import utils ; utils.re
import re
import enum
import string

def escape(x):
	return ''.join(
		(
			'\\'+i
			 if
			i in re.sre_parse.SPECIAL_CHARS
			 else
			i
		)
		for i in x
	)

def find_one(pattern, data):
	try:
		return re.findall(pattern, data)[0]
	except:
		if type(data) is str:
			return ''
		elif type(data) is bytes:
			return b''
		else:
			return []

class PATTERNS(enum.Enum):
	# hebrew[0] = \xd7\x90
	# hebrew[0] = \u05d0
	# hebrew[-1] = \xd7\xaa
	# hebrew[-1] = \u05ea
	# English + Hebrew alphabet only
	WORDS = re.compile("[a-zA-Z\u05d0-\u05ea]+")

	PUNCTUATIONS = re.compile(
		'['
		 +
		''.join([
			'\\' + i
			for i in
			string.punctuation
		])
		 +
		"]+"
	)

	# HEBREW_PUNCTUATIONS = re.compile("[\u05f2\u05f3\u05f4]+")
	HEBREW_PUNCTUATIONS = re.compile('[' + 
		''.join([
			'\u05f2', # HEBREW LIGATURE YIDDISH DOUBLE YOD
			'\u05f3', # GERESH
			'\u05f4'  # GERSHAYIM
		])
		 +
		"]+"
	)

	OLD_UNIOCDE = re.compile("[\ue000-\uefff]+")

	NUMBER = re.compile("[0-9]+")
		
	# H = "\xd7\x97"
	_H = "\u05d7"
	H = re.compile("(HH+)".replace('H', _H))

	OTHER = re.compile(
		'['
		 +
		''.join([
			'\xd7', # multiplication sign
			'\xe9', # e with accent
		])
		 +
		']'
	)

class UNICODE_PATTERNS(enum.Enum):
	EXTENDED_ASCII                        = re.compile("[\u0080-\u00ff]+")
	HEBREW                                = re.compile("[\u0590-\u05ff\ufb00-\ufb4f]+")
	ARABIC                                = re.compile("[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]+")
	GENERAL_PUNCTUATION                   = re.compile("[\u2000-\u206f]+")
	CURRENCY                              = re.compile("[\u20a0-\u20cf]+")
	MATHEMATICAL_OPERATORS                = re.compile("[\u2200-\u22ff]+")
	PRIVATE_USE                           = re.compile("[\ue000-\uf8ff]+")
	EMOTICONS                             = re.compile("[\U0001f600-\U0001f64f]+")
	MISCELLANEOUS_SYMBOLS_AND_PICTOGRAPHS = re.compile("[\U0001f300-\U0001f5ff]+")
