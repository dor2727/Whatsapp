import re
import sys
import time
import enum
import utils
import string
import datetime
import matplotlib.pyplot as plt

from collections import Counter


SUPPORTED_HOURS_DELTA = [0.5, 1, 2]


class MESSAGE_TYPE(enum.Enum):
	MESSAGE = 0
	MSG     = MESSAGE
	M       = MESSAGE
	MEDIA   = 1
	MD      = MEDIA
	SYSTEM  = 2
	SYS     = SYSTEM
	S       = SYSTEM
MT = utils.enum.enum_getter(MESSAGE_TYPE)

class MESSAGE_ITEMS(enum.Enum):
	DATE    = 0
	D       = DATE
	USER    = 1
	U       = USER
	MESSAGE = 2
	MSG     = MESSAGE
	M       = MESSAGE
	TYPE    = 3
	T       = TYPE
MI = utils.enum.enum_getter(MESSAGE_ITEMS)

class TIMESTEMP_ITEMS(enum.Enum):
	USER          = 0
	U             = USER
	ABSOLUTE_TIME = 1
	ABSOLUTE      = ABSOLUTE_TIME
	A             = ABSOLUTE_TIME
	RELATIVE_TIME = 2
	RELATIVE      = RELATIVE_TIME
	R             = RELATIVE_TIME
TI = utils.enum.enum_getter(TIMESTEMP_ITEMS)

class PATTERNS(enum.Enum):
	# split messages by the date pattern
	# "[date], [time] - .*"
	_DATE_AND_TIME = "\d{1,2}/\d{1,2}/\d\d, \d\d\:\d\d"
	DATE = re.compile(u'(' + _DATE_AND_TIME + " - .*)\n")

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
P = utils.enum.enum_getter(PATTERNS)

class UNICODE_PATTERNS(enum.Enum):
	EXTENDED_ASCII = re.compile("[\u0080-\u00ff]+")
	HEBREW = re.compile("[\u0590-\u05ff\ufb00-\ufb4f]+")
	ARABIC = re.compile("[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff]+")
	GENERAL_PUNCTUATION = re.compile("[\u2000-\u206f]+")
	CURRENCY = re.compile("[\u20a0-\u20cf]+")
	MATHEMATICAL_OPERATORS = re.compile("[\u2200-\u22ff]+")
	PRIVATE_USE = re.compile("[\ue000-\uf8ff]+")
	EMOTICONS = re.compile("[\U0001f600-\U0001f64f]+")
	MISCELLANEOUS_SYMBOLS_AND_PICTOGRAPHS = re.compile("[\U0001f300-\U0001f5ff]+")
UP = utils.enum.enum_getter(UNICODE_PATTERNS)

class Data(object):

	###############################################
	############          INIT         ############
	###############################################
	
	def init(self, debug=False, debug_time=None):
		if debug and not debug_time:
			debug_time = time.time()
		self.read_data()
		if debug:
			print("        [*] %.3f read_data done" % (time.time() - debug_time))
		self.parse_lines()
		if debug:
			print("        [*] %.3f parse_lines done" % (time.time() - debug_time))
		self.get_users()
		if debug:
			print("        [*] %.3f get_users done" % (time.time() - debug_time))
		self.get_all_words()
		if debug:
			print("        [*] %.3f get_all_words done" % (time.time() - debug_time))

	def init_all(self, debug=False):
		start = time.time()
		if debug:
			print("[*] init_all started")
			print("    [*] %.3f init started" % (time.time() - start))
			self.init(True, start)
		else:
			self.init()
		
		if debug:
			print("    [*] %.3f init done" % (time.time() - start))
		self.get_user_message_metadata()
		if debug:
			print("    [*] %.3f get_user_message_metadata done" % (time.time() - start))
		self.get_user_message_metadata(True)
		if debug:
			print("    [*] %.3f get_user_message_metadata done" % (time.time() - start))
		self.get_all_user_messages()
		if debug:
			print("    [*] %.3f get_all_user_messages done" % (time.time() - start))
		self.get_user_wpm()
		if debug:
			print("    [*] %.3f get_user_wpm done" % (time.time() - start))
		self.get_user_hpm()
		if debug:
			print("    [*] %.3f get_user_hpm done" % (time.time() - start))
		self.get_most_common_words()
		if debug:
			print("    [*] %.3f get_most_common_words done" % (time.time() - start))
		self.get_timestemps()
		if debug:
			print("    [*] %.3f get_timestemps done" % (time.time() - start))
		if debug:
			print("[*] loaded in %s seconds" % (time.time() - start))


	def read_data(self, file_name='w'):
		f = open(file_name, 'rb')
		a = f.read()
		f.close()
		self.data = a.decode("utf8")
		return self.data

	# returns [datetime, user, message, message_type]
	def parse_lines(self):
		"""
		parses the data and splits into messages
		message can be one of 3 types
			system message - "[date], [time] - [system_message_data]"
			user   message - "[date], [time] - [user]: [user_message_data]"
			user   media   - "[date], [time] - [user]: <Media omitted>"

		this data is being parsed into a 2D array
			1st dimension is the messages by order
			2nd dimension is a message tuple
				content name - [date    , user, message, message_type       ]
				content type - [datetime, str , str    , int of MESSAGE_TYPE]

		* ':' in a system message will return unwanted results
			e.g. "[user] has changed the group name to \"abc:def\""
		"""

		self.lines_raw = P("DATE").findall(self.data)

		self.lines = []
		for i in self.lines_raw:
			date, rest = i.split(" - ", 1)
			if ':' in rest:
				user, message = rest.split(": ", 1)
				# message_type = 1 if message == "<Media omitted>" else 0
				message_type = MT(int(message == "<Media omitted>"))
			else:
				user = "system"
				message = rest
				message_type = MT(2)

			temp_date_raw = re.findall("^(\d{1,2}/\d{1,2}/\d\d), ", date)[0]
			temp_date = utils.date.parse_date(temp_date_raw)
			temp_hour = date[date.find(',')+2:]
			temp_datetime = datetime.datetime(
				temp_date.year,
				temp_date.month,
				temp_date.day,
				int(temp_hour[:2]),
				int(temp_hour[-2:])
			)
			self.lines.append((
				temp_datetime, # date
				user,
				message,
				message_type
			))
		return self.lines

	# get the usernames list
	def get_users(self, first_name_only=False, anonymize=False):
		"""
		gets a unique list of all the users
		This functions' flags change the value of self.users and the return value
		However, these variables will exist anyway
			self._users_anonymized
			self._users
			self._users_first_name
		while self.users will be a copy of the list requested by the flags
		"""
		self.users = list(
					set(
						[i[MI("USER")] for i in self.lines]
					)
				)

		# set returns alphabetical order, list "shuffles" it
		# if anonymize: dont order
		# else: order
		if "system" in self.users:
			self.users.remove("system")

		### Anonymize ###
		# get the length of the list, the count how many digits it has by
		# converting it into string and counting its length
		self._user_name_format = "user%%0%dd" % len(str(len(self.users)))
		self._users_anonymized = [self._user_name_format % i for i in range(len(self.users))]
		
		self.users.sort()
		self._users = self.users[:]
		self._users_first_name = [
			(
				i[1:-1]
				 if
				i[0] == "\u202a"
				 and
				i[-1] == "\u202c"
				 else
				i.split()[0]
			)
			for i in self.users
		]

		if anonymize:
			self.users = self._users_anonymized[:] 
		else:
			if first_name_only:
				self.users = self._users_first_name[:]
		
		return self.users

	###############################################
	############        MESSAGES       ############
	###############################################

	# calculate amount of messages and percentage out of total messages
	def get_user_message_metadata(self, media=False):
		amount_of_user_messages = [
			len([
				i for i in self.lines
				if
					i[MI('USER')] == u
				and
					i[MI("TYPE")] == MT(int(media))
			])
			for u in self.users
		]

		messages_amount = sum(amount_of_user_messages)
		percent_of_messages = [float(i)/messages_amount for i in amount_of_user_messages]

		if media:
			self.user_media_amount = amount_of_user_messages
			self.user_media_percentage = percent_of_messages
		else:
			self.user_message_amount = amount_of_user_messages
			self.user_message_percentage = percent_of_messages

		return zip(self.users, amount_of_user_messages, percent_of_messages)
		# return [user, #messages, %messages]

	# get all the messages that the user sent
	def get_all_user_messages(self):
		self.messages_by_user = [
			[
				i[MI('MESSAGE')]
				for i in self.lines
				if
					i[MI("USER")] == u
				and
					i[MI("TYPE")] == MT(0)
			]
			for u in self.users
		]
		self.messages_by_user_combined = list(
			map(
				lambda x: '\n'.join(x),
				self.messages_by_user
			)
		)
		return self.messages_by_user

	def get_messages(self, message_filter):
		if "__call__" in dir(message_filter):
			filter_function = message_filter
		else:
			if "findall" in dir(message_filter):
				re_pattern = message_filter
			elif type(message_filter) is str:
				re_pattern = re.compile(message_filter)
			elif type(message_filter) is bytes:
				re_pattern = re.compile(message_filter.decode("utf8"))
			else:
				return(bool(print("Unknown message_filter type")))

			filter_function = lambda x: len(re_pattern.findall( x[MI("MESSAGE")] ))

		return list(filter(
			filter_function,
			self.lines
		))

	def get_following_messages(self, filter_function, amount=10, stop_after_another=True, exclude_function=None):
		messages = []
		# go through all the lines
		for index, i in enumerate(self.lines):
			# get only those that match the filter
			if filter_function(i): 
				
				# initiate empty following_messages list
				following_messages = [] 
				# this is used to count messages in addition to len(following_messages) for exclude_function use
				counter = 1 

				# keep adding until its full
				while len(following_messages) < amount and (index + counter) < len(self.lines):
					# stop_after_another
					if stop_after_another and filter_function(self.lines[index + counter]):
						break

					# exclude_function
					if exclude_function and exclude_function(self.lines[index + counter], i):
						counter += 1
						continue
					
					following_messages.append(self.lines[index + counter])
					counter += 1

				messages.append((i, following_messages))

		return messages

	###############################################
	############         WORDS         ############
	###############################################

	# get Words Per Message
	def get_user_wpm(self, ignore_short_messages=0):
		if not self.__dict__.get("messages_by_user"):
			get_all_user_messages(self.lines, self.users)
		self.user_wpm = [
			# join all the user messages, and then split by whitespace
			float( # get accurate division
				sum( # combine all the messages
					filter( # filter out messages shorter than wanted
						(lambda x: x > ignore_short_messages)
						 if
						ignore_short_messages
						 else
						None,
						map( # run on all the messages
							# change from message to amount of words in the message
							lambda x: len(x.split()),
							self.messages_by_user[i]
						)
					)
				)
			)
			 /
			len(self.messages_by_user[i])
			for i in range(len(self.users))
		]
		return self.user_wpm

	# get H Per Message
	def get_user_hpm(self):
		if not self.__dict__.get("messages_by_user_combined"):
			get_all_user_messages()
				# H Per Message

		all_user_h = list(map(P("H").findall, self.messages_by_user_combined))
		
		user_h_messages = list(map(len, all_user_h))
		self.user_h_amount = [len(''.join(h)) for h in all_user_h]

		# H per message
		self.user_hpm = list( # convert map to list
			map( # divide h_amount by user_message_amount
				lambda x: float(x[0]) / x[1],
				zip(
					self.user_h_amount,
					self.user_message_amount
				)
			)
		)

		# H per data (the whole string)
		self.user_hpd = [
			float(self.user_h_amount[i])
			 /
			len(self.messages_by_user_combined[i].replace(' ', ''))
			for i in range(len(self.users))
		]
		return all_user_h, user_h_messages, self.user_h_amount, self.user_hpm, self.user_hpd

	# create a list of all the words
	def get_all_words(self):
		self.words = sum([
			P("WORDS").findall(i[MI("MESSAGE")])
			for i in self.lines
			if i[MI("TYPE")] == MT(0) 
		], [])
		return self.words

	def get_most_common_words(self, amount=10, display=False):
		self.words_histogram = Counter(self.words)

		words = list(self.words_histogram.items())

		words.sort(key=lambda x: x[1]) # sort by the word

		if amount:
			words = words[-amount:]

		if display:
			print('\n'.join(["%04d - %s" % (i[1], i[0][::-1]) for i in words]))
		else:
			return words

	###############################################
	############         EMOJIS        ############
	###############################################

	def _get_non_letters(self, data=None):
		if not data:
			data = '\n'.join(self.messages_by_user_combined)
		data = re.sub(P("WORDS")                  , '', data)
		data = re.sub(P("PUNCTUATIONS")           , '', data)
		data = re.sub(P("HEBREW_PUNCTUATIONS")    , '', data)
		data = re.sub(P("NUMBER")                 , '', data)
		data = re.sub(P("OLD_UNIOCDE")            , '', data)
		data = re.sub(P("OTHER")                  , '', data)
		data = re.sub('\s'                        , '', data)
		data = re.sub(UP("EXTENDED_ASCII")        , '', data)
		data = re.sub(UP("HEBREW")                , '', data)
		data = re.sub(UP("ARABIC")                , '', data)
		data = re.sub(UP("GENERAL_PUNCTUATION")   , '', data)
		data = re.sub(UP("CURRENCY")              , '', data)
		data = re.sub(UP("MATHEMATICAL_OPERATORS"), '', data)
		data = re.sub(UP("PRIVATE_USE")           , '', data)
		# data = re.sub(UP("EMOTICONS")             , '', data)
		# data = re.sub(UP("MISCELLANEOUS_SYMBOLS_AND_PICTOGRAPHS"), '', data)
		return data
	
	def get_emoji_messages(self):
		return self.get_messages(utils.emoji.PATTERN)

	def get_all_emojis(self):
		return re.findall(utils.emoji.PATTERN, '\n'.join(self.messages_by_user_combined))
	def plot_all_emojis(self, amount=5):
		# a = wp.d.get_all_emojis()
		# b = Counter(a)
		# c = list(b.items())
		# d = list(map(lambda x:[wp.utils.emoji.emoji_to_hex(x[0]), x[1]], c))
		data = list(map(
			lambda x: [ utils.emoji.emoji_to_hex(x[0]), x[1] ],
			utils.counter(self.get_all_emojis())
		))
		return utils.plot.emoji_bar(
			data,
			amount=amount,
			sort=lambda x: x[1], # sort by the value of the word and not the amount
		)


	def get_all_user_emojis(self):
		pass

	###############################################
	############         CHATS         ############
	###############################################

	# return a list of (sender, absolute_time, relative_time)
	def get_timestemps(self):
		self.timestemps = []
		for index, x in enumerate(self.lines):
			if index:
				diff = self.lines[index][MI("DATE")] - self.lines[index - 1][MI("DATE")]
			else:
				diff = datetime.timedelta(0)
			self.timestemps.append([
				x[MI("USER")],
				x[MI("DATE")],
				diff
			])
		return self.timestemps

	def _print_timestemp(self, index, **kwargs):
		if type(index) is int:
			index = [index]
		if "__iter__" not in dir(index):
			return(bool(print("x needs to be int or list")))
		for x in index:
			r = self.timestemps[x][TI("RELATIVE")]
			print("%s : %s : %s" % (
				"%-20s" % self.timestemps[x][TI("USER")],
				self.timestemps[x][TI("ABSOLUTE")].strftime("%Y/%m/%d_%H:%M"),
				"%02dw_%02dd_%02d:%02d" % (r.days // 7, r.days % 7, r.seconds // (60*60), r.seconds // 60 % 60)
			), **kwargs)

###############################################
############        EXAMPLES       ############
###############################################

def plot_words(words, amount=15):
	utils.plot.hist(
		words, # the data
		sort=lambda x: x[1], # sort by the value of the word and not the amount
		amount=amount,
		map=lambda x: [x[0][::-1], x[1]] # hebrew display
	)

def whos_the_funniest(data):
	def is_media(x):
		return x[MI("TYPE")] == "MEDIA"
	def is_same_user(x,y):
		return x[MI("USER")] == y[MI("USER")]

	# get all the media messages
	all_media = data.get_following_messages(is_media, exclude_function=is_same_user)

	# reformat for our needs (the media message, all the following messages combined)
	all_media_formatter = [
		(
			i[0],
			'\n'.join([j[MI("MESSAGE")] for j in i[1]])
		)
		for i in all_media
	]

	media_h_amount = [
		(
			i[0],
			sum( # get the total amount of H
				map( # count amount per result of findall
					len, # count amount of H
					P("H").findall(i[1]) # get H out of all the messages
				)
			)
		)
		for i in all_media_formatter
	]

	user_h_per_media = [
		( # amount of H
			float( # of precise devision
				sum( # total amount of H
					map( # get only amount of H from each message
						lambda x: x[1],
						filter( # filter only messages by the user
							lambda x: x[0][MI("USER")] == u,
							media_h_amount
						)
					)
				)
			)
		)
		 /
		( # amount of messages by the user
			len( # count amount of messages
				list(filter( # filter only messages by the user
					lambda x: x[0][MI("USER")] == u,
					media_h_amount
				))
			)
		)
		for u in data._users
	]

	utils.plot.bar(user_h_per_media, data._users_first_name)

if __name__ == '__main__':
	pass
else:
	d = Data()
	d.init_all(True)
	