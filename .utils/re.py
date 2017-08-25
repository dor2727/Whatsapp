import re

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
