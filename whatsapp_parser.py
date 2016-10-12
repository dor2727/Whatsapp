import re
import sys
import time
import enum
import utils
import numpy
import string
import datetime
import matplotlib.pyplot as plt

from collections import Counter


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
	DATE     = 0
	D        = DATE
	USER     = 1
	U        = USER
	MESSAGE  = 2
	MSG      = MESSAGE
	M        = MESSAGE
	TYPE     = 3
	T        = TYPE
	RELATIVE = 4
	R        = RELATIVE
MI = utils.enum.enum_getter(MESSAGE_ITEMS)

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


def _get_non_letters(self, data):
	# data = '\n'.join(self.messages_by_user_combined)
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
	# I acctually don't remember why did I comment these lines
	# data = re.sub(UP("EMOTICONS")             , '', data)
	# data = re.sub(UP("MISCELLANEOUS_SYMBOLS_AND_PICTOGRAPHS"), '', data)
	return data

class Data(object):

	###############################################
	############          INIT         ############
	###############################################
	
	def init(self, debug=False, debug_time=None, exclude_system=True):
		if debug and not debug_time:
			debug_time = time.time()
		self._read_data()
		if debug:
			print("        [*] %.3f _read_data done" % (time.time() - debug_time))
		self.parse_lines(exclude_system=True)
		if debug:
			print("        [*] %.3f parse_lines done" % (time.time() - debug_time))
		self.create_users()
		if debug:
			print("        [*] %.3f create_users done" % (time.time() - debug_time))
		self.create_all_words()
		if debug:
			print("        [*] %.3f create_all_words done" % (time.time() - debug_time))

	def init_all(self, debug=False, exclude_system=True):
		start = time.time()
		if debug:
			print("[*] init_all started")
			print("    [*] %.3f init started" % (time.time() - start))
			self.init(True, start, exclude_system=True)
		else:
			self.init()
		
		if debug:
			print("    [*] %.3f init done" % (time.time() - start))
		self.create_user_message_metadata()
		if debug:
			print("    [*] %.3f create_user_message_metadata done" % (time.time() - start))
		self.create_user_message_metadata(True)
		if debug:
			print("    [*] %.3f create_user_message_metadata done" % (time.time() - start))
		self.create_all_user_messages()
		if debug:
			print("    [*] %.3f create_all_user_messages done" % (time.time() - start))
		self.create_user_wpm()
		if debug:
			print("    [*] %.3f create_user_wpm done" % (time.time() - start))
		self.create_user_hpm()
		if debug:
			print("    [*] %.3f create_user_hpm done" % (time.time() - start))
		self.create_chat_blocks()
		if debug:
			print("    [*] %.3f create_chat_blocks done" % (time.time() - start))
		
		if debug:
			print("[*] loaded in %s seconds" % (time.time() - start))

	def _read_data(self, file_name='w'):
		f = open(file_name, 'rb')
		a = f.read()
		f.close()
		self.data = a.decode("utf8")
		return self.data

	# returns [datetime, user, message, message_type, Relative_time]
	def parse_lines(self, exclude_system=True):
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

		last_time = None
		self.lines = []
		for i in self.lines_raw:
			date, rest = i.split(" - ", 1)
			if ':' in rest:
				user, message = rest.split(": ", 1)
				# message_type = 1 if message == "<Media omitted>" else 0
				message_type = MT(int(message == "<Media omitted>"))
			elif exclude_system:
				continue
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

			if last_time:
				diff = temp_datetime - last_time
				if diff < datetime.timedelta(0):
					diff = datetime.timedelta(0)
			else:
				diff = datetime.timedelta(0)
			last_time = temp_datetime

			self.lines.append((
				temp_datetime, # date
				user,
				message,
				message_type,
				diff
			))
		return self.lines

	# get the usernames list
	def create_users(self, first_name_only=False, anonymize=False):
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
		
	###############################################
	############        MESSAGES       ############
	###############################################

	# calculate amount of messages and percentage out of total messages
	def create_user_message_metadata(self, media=False):
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
	def create_all_user_messages(self):
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
		self.user_words_amount = list(map(len, self.messages_by_user_combined))
		return self.messages_by_user

	def get_messages(self, message_filter):
		# validate the message_filter parameter
		# a function
		if "__call__" in dir(message_filter):
			filter_function = message_filter
		# not a function -> needs to create one
		else:
			# already some re type
			if "findall" in dir(message_filter):
				re_pattern = message_filter
			# string
			elif type(message_filter) is str:
				re_pattern = re.compile(message_filter)
			# bytes
			elif type(message_filter) is bytes:
				re_pattern = re.compile(message_filter.decode("utf8"))
			else:
				return(bool(print("Unknown message_filter type")))

			filter_function = lambda x: bool(re_pattern.findall( x[MI("MESSAGE")] ))

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
	def create_user_wpm(self, ignore_short_messages=0):
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
	def create_user_hpm(self):
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
	def create_all_words(self):
		self.words = sum([
			P("WORDS").findall(i[MI("MESSAGE")])
			for i in self.lines
			if i[MI("TYPE")] == MT(0) 
		], [])
		self.words_histogram = utils.counter(self.words)
		return self.words

	def get_most_common_words(self, amount=10, display=False, top_first=False, multiple_lines=False):
		words = list(self.words_histogram) # copy

		words.sort(key=lambda x: x[1]) # sort by the word

		if amount:
			words = words[-amount:]

		if top_first:
			words = words[::-1]

		# if multiple_lines:
		# 	amount_per_line = multiple_lines // (max(map(
		# 		lambda x: len("%04d - %s" % (i[1], i[0][::-1])),
		# 		words
		# 	)) + 2)


		if display:
			print('\n'.join(["%04d - %s" % (i[1], i[0][::-1]) for i in words]))
		else:
			return words

	###############################################
	############         EMOJIS        ############
	###############################################
	
	def get_emoji_messages(self):
		return self.get_messages(utils.emoji.PATTERN)

	def get_all_emojis(self, combined=True):
		if combined:
			return re.findall(
				utils.emoji.PATTERN,
				'\n'.join(self.messages_by_user_combined)
			)
		else:
			return [
				re.findall(utils.emoji.PATTERN, i)
				for i in self.messages_by_user_combined
			]
	
	def plot_emojis(self, amount=5):
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
	def plot_emojis_by_users(self, amount=5):
		if len(self.users) != 2:
			return(bool(print("More than 2 users are not allowed!")))
		data = map(
			utils.counter,
			self.get_all_emojis(False)
		)
		data = map(
			lambda x: [
				[ utils.emoji.emoji_to_hex(i[0]), i[1] ]
				for i in x
			],
			data
		)
		return utils.plot.emoji_bar_2(
			list(data),
			amount=amount,
			sort=lambda x: x[1], # sort by the value of the word and not the amount
			title=self._users_first_name
		)

	###############################################
	############       EMOTICONS       ############
	###############################################

	def get_emoticon_messages(self):
		return self.get_messages(utils.smily.PATTERN)

	def get_emoticon_messages_by_type(self):
		return [
			self.get_messages(utils.smily.ER(i))
			for i in utils.smily.EMOTICON_NAMES
		]

	def get_all_emoticons(self, combined=True):
		if combined:
			return re.findall(
				utils.smily.PATTERN, 
				'\n'.join(self.messages_by_user_combined)
			)
		else:
			return [
				re.findall(utils.smily.PATTERN, i)
				for i in self.messages_by_user_combined
			]

	def plot_emoticons(self, amount=10):
		data = utils.counter(self.get_all_emoticons())
		return utils.plot.hist(
			data,
			amount=max(amount, len(data)),
			sort="counter"
		)
	def plot_emoticons_by_users(self, amount=5):
		if len(self.users) != 2:
			return(bool(print("More than 2 users are not allowed!")))
		data = map(
			utils.counter,
			self.get_all_emoticons(False)
		)
		return utils.plot.hist_2(
			list(data),
			amount=amount,
			sort="counter",
			title=self._users_first_name
		)
	def plot_emoticons_by_type(self):
		return utils.plot.hist(
			list(map(
				utils.smily.emoticon_to_type,
				self.get_all_emoticons()
			)),
			amount=len(utils.smily.EMOTICON_NAMES),
			sort="counter"
		)

	###############################################
	############         CHATS         ############
	###############################################

	def _print_timestemp(self, index=None, **kwargs):
		if index is None:
			index = range(len(self.lines))
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

	def create_chat_blocks(self):
		#############################
		#### utility functions   ####
		#############################

		#### division by time    ####

		timedelta_in_minutes = lambda x: x[MI("RELATIVE")].total_seconds() / 60
		tim = timedelta_in_minutes

		def is_night(x):
			"""
			on a normal work day, the average person sleeps at 10PM
			and wakes up at 8AM (or at least something like that..
			I haven't done any research in this topic)
			on a weekend day, the average person wakes up somewhere
			until 11AM
			thus, night >= 10PM or night <= 8AM
			which means that 8AM < day < 10PM
			which can be expressed as
				night = not (8AM < time < 10PM)
			# 8AM will be replaced by 11PM in case of a weekend
			"""
			_WEEKEND = [4,5] # 0 is monday, 4,5 is friday,saturday
			return not (11 if x[MI("DATE")].weekday() in _WEEKEND else 8) < x[MI("DATE")].hour < 22
		def is_after_night(x):
			"""
			allow the message to be up to 2 hours after the wake-up
			Other ideas : 
				check if this is a different user
				check if there is a reasonable time difference
			"""
			_WEEKEND = [4,5] # 0 is monday, 4,5 is friday,saturday
			morning = (11 if x[MI("DATE")].weekday() in _WEEKEND else 8)
			morning += 2
			after_night = (
				x[MI("DATE")].hour < morning
				 or
				x[MI("DATE")].hour > 22
			)
			return after_night

		#### division by sender  ####

		def amount_of_senders(x):
			return len(set( i[MI("USER")] for i in x ))
		def is_single_sender(x):
			return amount_of_senders(x) == 1
		def is_being_ignored(index):
			"""
			checks whether the first message of the next chat block is more than 24h apart
			checks whether the first message of the next chat block is from the same
				user as the last message of the current chat block
			"""
			# this is the first message, it can't be ignored
			if not index:
				return False

			# check how far is the first message of the next chat block
			if chats[index+1][0][MI("RELATIVE")].total_seconds() > 24*60*60:
				# the other side ignored your message
				ignored_by_time = True
			else:
				# this is a normal single-sender chat-block
				ignored_by_time = False

			# check if the sender of the end of this chat block is
			# the same as the sender of the beginning of the next chat block
			if is_single_sender((chats[index][-1], chats[index+1][0])):
				# this is the same person after some delay
				ignored_by_sender = True
			else:
				# this is the other person answering
				ignored_by_sender = False

			return ignored_by_time or ignored_by_sender

		#############################
		#### division by time    ####
		#############################
		#### main loop           ####
		#############################
		chats = []
		current_chat = []
		for i, line in enumerate(self.lines):
			# less then half an hour apart
			if tim(line) < 60:
				current_chat.append(line)
			# more then a day apart
			elif 24*60 < tim(line):
				chats.append(current_chat)
				current_chat = [line]
			# sent while the other person was sleeping
			elif (
				i
				 and
				is_night(self.lines[i-1])
				 and
				is_after_night(line)
				 and
				not is_single_sender((line, self.lines[i-1]))
			):
				current_chat.append(line)
			# default
			else:
				chats.append(current_chat)
				current_chat = [line]

		self.raw_chats = chats[:]

		#############################
		#### division by sender  ####
		#############################
		#### main loop           ####
		#############################
		# the last chat is a special case and will be treated later

		"""
		if current_chat is single_sender, it is possible that is should be appended to the
		next chat-block. Another criteria stands in the way, though.
		what if the last message in the current chat-block is being ignored?
		it can be verified in 2 ways
			if the next message is more than 24h away
			if the next message is from the last sender
				(we can assume that if the messages are on different
				 chat blocks, they are far enough from each other)
		note - this does not handle the case where the single-sender chat-block should be added to the previous
			chat, though this is less common, and I think that I can handle this statistical flaw
		"""
		chats_to_append_to_next = list(map(
				lambda index: (
					is_single_sender(chats[index])
					 and
					not is_being_ignored(index)
				),
				range(len(chats) - 1) # remove the last chat
			)) + [False]

		index = 0
		while index < len(chats_to_append_to_next) - 1:
			if chats_to_append_to_next[index]:
				# combine the current and next chats to a single chat
				chats[index : index+2] = [chats[index] + chats[index+1]]
				chats_to_append_to_next.pop(index)
				index -= 1
			index += 1

		# the last chat is a special case since it does not have a next chat
		# thus, if the last chat is a single-sender, it will be combined with
		# the previous chat
		if is_single_sender(chats[-1]):
			chats[-2:] = [chats[-2]+chats[-1]]

		self.chats = chats

	def _print_chat(self, i):
		if type(i) is int:
			i = self.chats[i]
		print('\n'.join(map(
			lambda x: "%-6s - %s (%6.2f) - %s" % (
				x[1].split()[0], # sender
				x[0].strftime("%Y/%m/%d_%H:%M"), # date
				x[4].total_seconds() / 60**2, # diff
				x[2][::-1] # message
			),
			i
		)))

	###############################################
	############       FEATURES        ############
	###############################################

	def get_all_features(self):
		if len(self.users) != 2:
			return(bool(print("len(users) != 2")))
		features = {}

		##### message ratio #####
		
		features["message ratio"]      = numpy.divide(*self.user_message_amount)
		features["media ratio"]        = numpy.divide(*self.user_media_amount)
		features["words ratio"] = numpy.divide(*list(map(len, self.messages_by_user_combined)))
		
		_long_messages = self.get_messages(lambda x:len(x[MI('M')].split()>=10))
		_long_messages_amount_per_user = list(map(
			# iterate all the users
			# and count how many long messages each of them has
			lambda u: len(list(filter(
				# iterate all the long messages
				# and filter out only messages by the user
				lambda m: m[MI('U')] == u,
				_long_messages
			))),
			self.users
		))
		features["long message ratio"] = numpy.divide(*_long_messages_amount_per_user)
		del _long_messages
		del _long_messages_amount_per_user

		##### laugher #####

		features["h / message"]
		features["messages with h"]
		features["amount of h after media"]

		##### basic time statistics #####

		features["most active hours"]
		features["most active days"]
		features["chat timespan"]
		features["message / day"]
		features["message / week"]
		features["message / month"]
		features["media / day"]
		features["media / week"]
		features["media / month"]
		features["words / day"]
		features["words / week"]
		features["words / month"]

		##### advanced time statistics #####

		##### emoji #####
		
		features["emoji / message"] = list(map(
			lambda x: x,
			self.users
		))

	def get_all_features(self):
		ratio = {}
		ratio["message"] = numpy.divide(*self.user_message_amount)
		ratio["media"] = numpy.divide(*self.user_media_amount)
		ratio["words"] = numpy.divide(*self.user_words_amount)

		_long_messages = self.get_messages(lambda x:len(x[MI('M')].split()>=10))
		_long_messages_amount_per_user = list(map(
			# iterate all the users
			# and count how many long messages each of them has
			lambda u: len(list(filter(
				# iterate all the long messages
				# and filter out only messages by the user
				lambda m: m[MI('U')] == u,
				_long_messages
			))),
			self.users
		))
		ratio["long messages"] = numpy.divide(*_long_messages_amount_per_user)
		del _long_messages
		del _long_messages_amount_per_user

		_messages_with_h = self.get_messages(P("H"))
		_messages_with_h_per_user = list(map(
			lambda u: len(list(filter(
				lambda m: m[MI('U')] == u,
				_messages_with_h
			))),
			self.users
		))
		ratio["messages with h"] = numpy.divide(*_messages_with_h_per_user)

		laugh = {}
		laugh["user0 hpm"] = self.user_hpm[0]
		laugh["user1 hpm"] = self.user_hpm[1]
		_user_h_per_media = whos_the_funniest(self, plot=False)
		laugh["user0 h after media"] = _user_h_per_media[1]
		laugh["user1 h after media"] = _user_h_per_media[1]
		del _user_h_per_media

		active_hours = dict(zip(["07-12", "12-17", "17-21", "21-07"], [0]*4))
		for i in self.lines:
			if   7  <= i[MI("DATE")].hour < 12:
				active_hours["07-12"] += 1
			elif 12 <= i[MI("DATE")].hour < 17:
				active_hours["12-17"] += 1
			elif 17 <= i[MI("DATE")].hour < 21:
				active_hours["17-21"] += 1
			else:
				active_hours["21-07"] += 1
		for k in active_hours:
			active_hours[k] /= len(self.lines)

		_active_days = [0]*len(utils.date.DAYS)
		for i in self.lines:
			_active_days[i[0].weekday()] += 1
		active_days = dict(zip(
			utils.date.DAYS, 
			map(
				lambda x: x / len(self.lines),
				_active_days
			)
		))
		del _active_days

		user0_activity_per_day = {}
		user1_activity_per_day = {}
		total_activity_per_day = {}
		user0_activity_per_message = {}
		user1_activity_per_message = {}

		_chat_length = (self.lines[-1][0] - self.lines[0][0]).days
		user0_activity_per_day["message"] = self.user_message_amount[0] / _chat_length
		user1_activity_per_day["message"] = self.user_message_amount[1] / _chat_length
		total_activity_per_day["message"] = sum(self.user_message_amount)   / _chat_length

		user0_activity_per_day["media"] = self.user_media_amount[0] / _chat_length
		user1_activity_per_day["media"] = self.user_media_amount[1] / _chat_length
		total_activity_per_day["media"] = sum(self.user_media_amount)   / _chat_length

		user0_activity_per_day["words"] = self.user_words_amount[0] / _chat_length
		user1_activity_per_day["words"] = self.user_words_amount[1] / _chat_length
		total_activity_per_day["words"] = sum(self.user_words_amount)   / _chat_length

		_emojis_per_user = list(map(len, self.get_all_emojis(False)))
		user0_activity_per_day["emoji"] = _emojis_per_user[0] / _chat_length
		user1_activity_per_day["emoji"] = _emojis_per_user[1] / _chat_length
		total_activity_per_day["emoji"] = sum(_emojis_per_user) / _chat_length
		user0_activity_per_message["emoji"] = _emojis_per_user[0] / self.user_message_amount[0]
		user1_activity_per_message["emoji"] = _emojis_per_user[1] / self.user_message_amount[1]
		del _emojis_per_user

		_emoticons_per_user = list(map(len, self.get_all_emoticons(False)))
		user0_activity_per_day["emoticons"] = _emoticons_per_user[0] / _chat_length
		user1_activity_per_day["emoticons"] = _emoticons_per_user[1] / _chat_length
		total_activity_per_day["emoticons"] = sum(_emoticons_per_user) / _chat_length
		user0_activity_per_message["emoticons"] = _emoticonss_per_user[0] / self.user_message_amount[0]
		user1_activity_per_message["emoticons"] = _emoticonss_per_user[1] / self.user_message_amount[1]
		del _emoticons_per_user

		conversations = {}
		conversations["amount per week"] = len(self.chats) // (_chat_length//7)
		ratio["conversations"] = numpy.divide(*
			[
				i[1]
				for i in [
					utils.counter([
						i[0][MI("USER")]
						for i in self.chats
					])
				]
			]
		)


def print_line(x):
	print("%-6s - %s (%6.2f) - %s" % (
		x[1].split()[0], # sender
		x[0].strftime("%Y/%m/%d_%H:%M"), # date
		x[4].total_seconds() / 60**2, # diff
		x[2][::-1] # message
	))

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

def whos_the_funniest(data, plot=True):
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

	if plot:
		utils.plot.bar(user_h_per_media, data._users_first_name)
	else:
		return user_h_per_media

if __name__ == '__main__':
	pass
else:
	d = Data()
	d.init_all(debug=True, exclude_system=True)
	