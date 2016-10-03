def print_chat(i):
	print('\n'.join(map(
		lambda x: "%-6s - %s (%6.2f) - %s" % (
			x[1].split()[0], # sender
			x[0].strftime("%Y/%m/%d_%H:%M"), # date
			x[4].total_seconds() / 60**2, # diff
			x[2][::-1] # message
		),
		i
	)))


