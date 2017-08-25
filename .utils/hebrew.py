import os
import sys

HEBREW = {
	'q'  : '/' ,
	'w'  : '\'',
	'e'  : 'ק' ,
	'r'  : 'ר' ,
	't'  : 'א' ,
	'y'  : 'ט' ,
	'u'  : 'ו' ,
	'i'  : 'ן' ,
	'o'  : 'ם' ,
	'p'  : 'פ' ,
	'a'  : 'ש' ,
	's'  : 'ד' ,
	'd'  : 'ג' ,
	'f'  : 'כ' ,
	'g'  : 'ע' ,
	'h'  : 'י' ,
	'j'  : 'ח' ,
	'k'  : 'ל' ,
	'l'  : 'ך' ,
	';'  : 'ף' ,
	'\'' : ',' ,
	'z'  : 'ז' ,
	'x'  : 'ס' ,
	'c'  : 'ב' ,
	'v'  : 'ה' ,
	'b'  : 'נ' ,
	'n'  : 'מ' ,
	'm'  : 'צ' ,
	','  : 'ת' ,
	'.'  : 'ץ' ,
	'/'  : '.'
}

def replace(x):
	for i in HEBREW:
		x = x.replace(i, HEBREW[i])

	return x

if __name__ == '__main__':
	if len(sys.argv) == 2 and sys.argv[1] in ["--help", "-h", "-?", "/?", "/h", "/help"]:
		exit(bool(print("USAGE : %s [-i / --interactive] Or [string to translate]" % sys.argv[0])))

	elif len(sys.argv) == 2 and sys.argv[1] in ["--interactive", "-i"]:
		try:
			while 1:
				a = input("> ")
				print(replace(a))
		except KeyboardInterrupt as e:
			exit(1)

	else:
		print(replace(' '.join(sys.argv[1:])))
