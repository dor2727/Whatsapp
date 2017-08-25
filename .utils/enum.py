import enum

def enum_getter(enum_class):
	def getter(x):
		if type(x) is str:
			if x == '*':
				return {i.name:i.value for i in list(x)}
			else:
				return enum_class[x.upper()].value
		elif type(x) is int:
			return enum_class(x).name
		else:
			return(bool(print(enum_class.__name__ + " key error")))

	return getter