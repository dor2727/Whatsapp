from collections import Counter

def counter(data):
	return list(Counter(data).items())

def roof(x, y):
	i = x.__divmod__(y)
	return i[0] + bool(i[1])

_rl = lambda x: range(len(x))

def get_current_memory(in_mb=False):
	_scale = {	'kB': 1024.0, 'mB': 1024.0*1024.0,
          		'KB': 1024.0, 'MB': 1024.0*1024.0}
	a = open("/proc/self/status").read()
	b = a[a.find("VmSize:"):].split(None, 3) # split by whitespace
	mem = float(b[1]) * _scale[b[2]]
	return mem / 1024.0**2 if in_mb else mem

class Debug():
	def __init__(self, debug=True):
		self.debug=debug
	def print(self, msg, tab=0):
		if not self.debug:
			return

		if type(tab) is int:
			if type(msg) is str:
				tab = ' ' * 4 * tab
			if type(msg) is bytes:
				tab = b' ' * 4 * tab
		if type(msg) is str and type(tab) is bytes:
			tab = tab.decode()
		if type(msg) is bytes and type(tab) is str:
			tab = tab.encode()

		print(tab + msg)
