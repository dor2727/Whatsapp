#!/usr/bin/env python3
import re
import sys
import time
import enum
import utils
import numpy
import datetime
import matplotlib.pyplot as plt

from collections import Counter

P  = utils.enum.enum_getter(utils.re.PATTERNS)
UP = utils.enum.enum_getter(utils.re.UNICODE_PATTERNS)

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
	USER     = 0
	U        = USER
	MESSAGE  = 1
	MSG      = MESSAGE
	M        = MESSAGE
	TYPE     = 2
	T        = TYPE
	DATE     = 3
	D        = DATE
	RELATIVE = 4
	R        = RELATIVE
MI = utils.enum.enum_getter(MESSAGE_ITEMS)

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

class Line(object):
	"""
	parses the data and splits into messages
	message can be one of 3 types
		system message - "[date], [time] - [system_message_data]"
		user   message - "[date], [time] - [user]: [user_message_data]"
		user   media   - "[date], [time] - [user]: <Media omitted>"

	this data is being parsed into an array
		content name - [date    , user, message, message_type       ]
		content type - [datetime, str , str    , int of MESSAGE_TYPE]

	* ':' in a system message will return unwanted results
		e.g. "[user] has changed the group name to \"abc:def\""
	"""

		# split messages by the date pattern
	# "[date], [time] - .*"
	_DATE = "\\d{1,2}/\\d{1,2}/\\d\\d"
	_TIME = "\\d\\d\:\\d\\d"
	_DATE_AND_TIME = "%s, %s" % (_DATE, _TIME)
	DATE = re.compile(u"(%s - .*)\n" % _DATE_AND_TIME)


	def __init__(self, s, prev_time=None):
		self._raw = s
		self.parse(prev_time)

	def __getitem__(self, index):
		return self.data[index]

	def parse(self, prev_time):
		date, rest = self._raw.split(" - ", 1)
		if ':' in rest:
			user, message = rest.split(": ", 1)
			# message_type = 1 if message == "<Media omitted>" else 0
			message_type = MT(int(message == "<Media omitted>"))
		else:
			user = "system"
			message = rest
			message_type = "SYSTEM"

		temp_date_raw = re.findall("^(%s), " % self._DATE, date)[0]
		temp_date = utils.date.parse_date(temp_date_raw)
		temp_time = date.split(", ")[1]
		temp_datetime = datetime.datetime(
			temp_date.year,
			temp_date.month,
			temp_date.day,
			int(temp_time[:2]),
			int(temp_time[-2:])
		)

		if prev_time is None:
			diff = datetime.timedelta(0)
		else:
			diff = temp_datetime - prev_time
			if diff < datetime.timedelta(0):
				diff = datetime.timedelta(0)


		self.user          = user
		self.message       = message
		self.message_type  = message_type
		self.date          = temp_datetime
		self.relative_date = diff
		self.data = [
			self.user          ,
			self.message       ,
			self.message_type  ,
			self.date          ,
			self.relative_date ,
		]

class Data(object):

	###############################################
	############          INIT         ############
	###############################################

	def __init__(self, file_name="data/w", debug=True):
		self._file_name = file_name
		self.debug = utils.Debug(debug)
	
	def init(self, exclude_system=True, start_time=None, tab=0):
		start = start_time or time.time()
		self._read_data()
		self.debug.print(tab=tab, msg="[*] %.3f _read_data done"       % (time.time() - start))

		self.parse_lines(exclude_system=True)
		self.debug.print(tab=tab, msg="[*] %.3f parse_lines done"      % (time.time() - start))

		self.create_users()
		self.debug.print(tab=tab, msg="[*] %.3f create_users done"     % (time.time() - start))

		self.create_all_words()
		self.debug.print(tab=tab, msg="[*] %.3f create_all_words done" % (time.time() - start))

	def init_all(self, exclude_system=True):
		start = time.time()
		self.debug.print(tab=0, msg="[*] init_all started")

		self.debug.print(tab=1, msg="[*] %.3f init started"                      % (time.time() - start))
		self.init(exclude_system=exclude_system, start_time=start, tab=2)
		self.debug.print(tab=1, msg="[*] %.3f init done"                         % (time.time() - start))

		self.create_user_message_metadata()
		self.debug.print(tab=1, msg="[*] %.3f create_user_message_metadata done" % (time.time() - start))

		self.create_user_media_metadata()
		self.debug.print(tab=1, msg="[*] %.3f create_user_media_metadata done"   % (time.time() - start))

		self.create_all_user_messages()
		self.debug.print(tab=1, msg="[*] %.3f create_all_user_messages done"     % (time.time() - start))

		self.create_user_wpm()
		self.debug.print(tab=1, msg="[*] %.3f create_user_wpm done"              % (time.time() - start))

		self.create_user_hpm()
		self.debug.print(tab=1, msg="[*] %.3f create_user_hpm done"              % (time.time() - start))

		self.create_chat_blocks()
		self.debug.print(tab=1, msg="[*] %.3f create_chat_blocks done"           % (time.time() - start))
		
		self.debug.print(tab=0, msg="[*] loaded in %s seconds"                   % (time.time() - start))

	def _read_data(self):
		self.data = open(self._file_name, 'rb').read().decode("utf8")

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

		self.lines_raw = Line.DATE.findall(self.data)

		last_time = None
		self.lines = []
		for i in self.lines_raw:
			temp = Line(i, last_time)

			self.lines.append(temp)
			last_time = temp.date

		return True

	# get the usernames list
	def create_users(self, first_name_only=False, anonymize=False):
		"""
		gets a unique list of all the users
		This functions' flags change the value of self.users
		However, these variables will exist anyway
			self._users_anonymized
			self._users_full_name
			self._users_first_name
		while self.users will be a copy of the list requested by the flags
		"""

		# set returns alphabetical order, list "shuffles" it
		# if anonymize: dont order
		# else: order
		self.users = list(set( i.user for i in self.lines ))

		if "system" in self.users:
			self.users.remove("system")

		### Anonymize ###
		# get the length of the list, the count how many digits it has by
		# converting it into string and counting its length
		self._user_name_format = "user%%0%dd" % len(str(len(self.users)))
		self._users_anonymized = [self._user_name_format % i for i in range(len(self.users))]
		
		self.users.sort()
		self._users_full_name  = self.users[:]
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

	# calculate amount of text-messages and percentage out of total text-messages
	def create_user_message_metadata(self):
		self.user_message_amount = [0]*len(self.users)
		for i in filter(
			lambda l: l.message_type == "MESSAGE",
			self.lines
		):
			self.user_message_amount[self._users_full_name.index(i.user)] += 1

		amount_of_user_messages = sum(self.user_message_amount)
		self.user_message_percentage = [float(i)/amount_of_user_messages for i in self.user_message_amount]

	# calculate amount of media-messages and percentage out of total media-messages
	def create_user_media_metadata(self):
		self.user_media_amount = [0]*len(self.users)
		for i in filter(
			lambda l: l.message_type == "MEDIA",
			self.lines
		):
			self.user_media_amount[self._users_full_name.index(i.user)] += 1

		amount_of_user_media = sum(self.user_media_amount)
		self.user_media_percentage = [float(i)/amount_of_user_media for i in self.user_media_amount]

	# get all the messages that the user sent
	def create_all_user_messages(self):
		self.messages_by_user = [
			[
				i.message
				for i in self.lines
				if
					i.user == u
				and
					i.message_type == "MESSAGE"
			]
			for u in self._users_full_name
		]
		self.messages_by_user_combined = list(
			map(
				'\n'.join,
				self.messages_by_user
			)
		)
		self.user_words_amount = list(map(
			lambda x: len(x.split()),
			self.messages_by_user_combined
		))

	def get_messages(self, message_filter=None):
		# validate the message_filter parameter
		# all messages
		if message_filter is None:
			# return a generator of self.lines
			return (i for i in self.lines)
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

		return filter(
			filter_function,
			self.lines
		)

	def get_following_messages(self, filter_function, amount=10, stop_after_another=True, exclude_function=None):
		"""
		filter_function  = lambda line(str): bool
		exclude_function = lambda next_line(str), prev_line(str): bool
		"""
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
		"""
		count the total amount of words,
		from all the messages sent by the user
		which has more than ignore_short_messages words
		if ignore_short_messages > 0
		else, from all the messages
		and divide by the amount of messages
		"""
		return [
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

	# a create function, hust for the convension
	def create_user_wpm(self):
		self.user_wpm = self.get_user_wpm()

	# get H Per Message
	def create_user_hpm(self):
		# a list of all the H's ever sent by each user
		all_user_h = list(map(
			P("H").findall,
			self.messages_by_user_combined
		))
		
		# total H's sent by each user
		self.user_h_amount = [
			sum(map(len, user_h))
			for user_h in all_user_h
		]

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
			len(
				# ''.join(data.split) - remove whitespace
				''.join( self.messages_by_user_combined[i].split() )
			)
			for i in range(len(self.users))
		]

	# create a list of all the words
	def create_all_words(self):
		self.words_all = sum([
			P("WORDS").findall(i.message)
			for i in self.lines
			if i.message_type == "MESSAGE"
		], [])
		self.words_histogram = utils.counter(self.words_all)
		self.words_unique = list(set(self.words_all))
		self.words_unique.sort()

	def get_most_common_words(self, amount=10, display=False, top_first=True):
		words = list(self.words_histogram) # copy

		words.sort(key=lambda x: x[1]) # sort by the word

		if amount:
			words = words[-amount:]

		if top_first:
			words = words[::-1]

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
			combine = lambda x: sum(x, [])
		else:
			combine = lambda x: x

		return combine([
			re.findall(utils.emoji.PATTERN, i)
			for i in self.messages_by_user_combined
		])
	
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

	def get_features_ratio(self):
		ratio = {}
		ratio_description = {}

		# message ratio
		ratio_description["message"] = "[amount of messages from] user0 / user1"
		ratio["message"] = numpy.divide(*self.user_message_amount)

		# media ratio
		ratio_description["media"] = "[amount of media from] user0 / user1"
		ratio["media"] = numpy.divide(*self.user_media_amount)

		# words ratio
		ratio_description["words"] = "[amount of words sent by] user0 / user1"
		ratio["words"] = numpy.divide(*self.user_words_amount)

		# long_messages ratio
		ratio_description["long messages"] = "[amount of messages with more than 10 words from] user0 / user1"
		_long_messages = self.get_messages(lambda x:len(x[MI('M')].split())>=10)
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

		# messages with h
		ratio_description["messages with h"] = "[amount of messages with h by] user0 / user1"
		_messages_with_h = self.get_messages(P("H"))
		_messages_with_h_per_user = list(map(
			lambda u: len(list(filter(
				lambda m: m[MI('U')] == u,
				_messages_with_h
			))),
			self.users
		))
		ratio["messages with h"] = numpy.divide(*_messages_with_h_per_user)
		del _messages_with_h
		del _messages_with_h_per_user

		ratio_description["conversations"] = "[amount of conversations started by] user0 / user1"
		_conversations_started = utils.counter([
				c[0][MI("USER")]
				for c in self.chats
			])
		ratio["conversations"] = numpy.divide(*[
			# get the conversation started by the user
			next(filter(
				lambda x: x[0] == u,
				_conversations_started
			# get the amount of conversations
			))[1]
			for u in
			# keep the order of the users
			self.users
		])
		
		return ratio, ratio_description

	def get_features_laugh(self):
		laugh = {}
		laugh_description = {}

		# H per message
		# H per data
		laugh_description["user%d hpm"] = "H per message of every user"
		laugh_description["user%d hpd"] = "H per [amount of chars] of every user"
		for i in range(len(self.users)):
			laugh["user%d hpm" % i] = self.user_hpm[i]
			laugh["user%d hpd" % i] = self.user_hpd[i]

		# H after media
		laugh_description["user%d h after media"] = "amount of H coming from other users for media sent by the user (indicates how funny the media is)"
		_user_h_per_media = whos_the_funniest(self, plot=False, following_messages_amount=5)
		for i in range(len(self.users)):
			laugh["user%d h after media" % i] = _user_h_per_media[i]
		del _user_h_per_media

		return laugh, laugh_description

	def get_features_basic_time_statistics_general(self):
		# active hours
		active_hours_description = {
			'*'     : "A dict showing the active times of the day in percentages.\n"
			          "They all add up to 1 (sum(active_hours.values()) ~= 1 # up to float precision )",
			"07-12" : "Morning",
			"12-17" : "Noon",
			"17-21" : "Evening",
			"21-07" : "Night"
		}
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

		# active days
		active_days_description = "Percentage of activity in each day (0 is Monday)"
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

		return  active_hours, active_hours_description, \
				active_days, active_days_description

	def get_features_basic_time_statistics_per_user(self):
		activity = {}
		for i in range(len(self.users)):
			activity["user%d" % i] = {}
			# activity of user per day
			activity["user%d" % i]["day"] = {}
			# activity of user per message
			activity["user%d" % i]["message"] = {}
		activity["total"] = {}
		activity["total"]["day"] = {}
		activity["total"]["message"] = {}

		# how long is the chat (in days)
		_chat_length = (self.lines[-1][0] - self.lines[0][0]).days

		# [message / media / words] per day
		for i in range(len(self.users)):
			activity["user%d" % i]["day"]["message"] = self.user_message_amount[i] / _chat_length
			activity["user%d" % i]["day"]["media"]   = self.user_media_amount[i]   / _chat_length
			activity["user%d" % i]["day"]["words"]   = self.user_words_amount[i]   / _chat_length
		activity["total"]["day"]["message"] = sum(self.user_message_amount)   / _chat_length
		activity["total"]["day"]["media"]   = sum(self.user_media_amount)     / _chat_length
		activity["total"]["day"]["words"]   = sum(self.user_words_amount)     / _chat_length

		_emojis_per_user    = list(map(len, self.get_all_emojis   (combined=False)))
		_emoticons_per_user = list(map(len, self.get_all_emoticons(combined=False)))
		for i in range(len(self.users)):
			activity["user%d" % i]["day"]    ["emoji"]    = _emojis_per_user[i]    / _chat_length
			activity["user%d" % i]["message"]["emoji"]    = _emojis_per_user[i]    / self.user_message_amount[i]
			activity["user%d" % i]["day"]    ["emoticon"] = _emoticons_per_user[i] / _chat_length
			activity["user%d" % i]["message"]["emoticon"] = _emoticons_per_user[i] / self.user_message_amount[i]
		activity["total"]["day"]    ["emoji"] = sum(_emojis_per_user) / _chat_length
		activity["total"]["message"]["emoji"] = sum(_emojis_per_user) / sum(self.user_message_amount)
		activity["total"]["day"]    ["emoticon"] = sum(_emoticons_per_user) / _chat_length
		activity["total"]["message"]["emoticon"] = sum(_emoticons_per_user) / sum(self.user_message_amount)
		del _emojis_per_user
		del _emoticons_per_user
		del _chat_length

		return activity

	def get_features_conversations(self):
		conversations = {}
		conversations_description = {}

		### utility functions
		def _amount_of_senders(x):
			return len(set( i[MI("USER")] for i in x ))
		def get_multi_user_chats():
			return filter(
				lambda x: _amount_of_senders(x) > 1,
				self.chats
			)
		def count_multi_user_chats():
			return sum(map(
				lambda x: _amount_of_senders(x) > 1,
				self.chats
			))
		def get_user_started_chats(index):
			return filter(
				lambda x: x[0][MI("USER")] == self.users[index],
				get_multi_user_chats()
			)
		def get_index_of_first_message_of_second_user(chat):
			"""
			next makes it so only the first output
			of the filter object is returned
			and than the gc deletes the filter object
			"""
			return chat.index(next(filter(
				lambda x: x[MI("USER")] != chat[0][MI("USER")],
				chat
			)))

		# how long is the chat (in days)
		_chat_length = (self.lines[-1][0] - self.lines[0][0]).days

		# conversations per week
		conversations_description["week"] = "amount of conversations per week"
		conversations["week"] = len(self.chats) / (_chat_length//7)
		# not-ignored conversations per week
		conversations_description["week 1<"] = "amount of (conversations with more than 1 sender) per week"
		conversations["week 1<"] = count_multi_user_chats() / (_chat_length//7)
		del _chat_length

		# diff time between conversations
		_diff_time_between_conversations = list(map(
			lambda x: x[0][MI("RELATIVE")].total_seconds(),
			self.chats[1:]
		))
		conversations_description["avg diff time"] = "average of diff time between following conversations"
		conversations_description["std diff time"] = "standard deviation of diff time between following conversations"
		conversations["avg diff time"] = numpy.average(_diff_time_between_conversations)
		conversations["std diff time"] = numpy.std(_diff_time_between_conversations)
		del _diff_time_between_conversations

		# amount of ignored chats
		conversations_description["user%d ignored chats"] = "amount of conversations user%d started and the other user ignored"
		_ignored_chats = [0]*len(self.users)
		for c in self.chats:
			if _amount_of_senders(c) == 1:
				_ignored_chats[
					self.users.index(
						c[0][MI("USER")]
					) 
				] += 1
		for i in range(len(self.users)):
			conversations["user%d ignored chats" % i] = _ignored_chats[i] / len(self.chats)
		del _ignored_chats

		# diff time between first sender to second sender
		#     where user%d is the first sender
		conversations_description["user%d avg between messages"] = "average of the time between the message of user%d that started the conversation to the reply message of the other user"
		conversations_description["user%d std between messages"] = "standard deviation of the time between the message of user%d that started the conversation to the reply message of the other user"
		for u in range(len(self.users)):
			diffs = []
			for c in get_user_started_chats(u):
				i = get_index_of_first_message_of_second_user(c)
				diff = c[i][MI("DATE")] - c[i-1][MI("DATE")]
				diffs.append(diff.total_seconds())
			conversations["user%d avg between messages" % u] = numpy.average(diffs)
			conversations["user%d std between messages" % u] = numpy.std(diffs)

		conversations_description["emotions"] = "average amount of emojis and emoticons in conversations"
		conversations["emotions"] = sum(map(
			lambda c: len(
				re.findall(utils.emoji.PATTERN, '\n'.join(i[MI("MESSAGE")] for i in c))
				 +
				re.findall(utils.smily.PATTERN, '\n'.join(i[MI("MESSAGE")] for i in c))
			),
			self.chats
		)) / len(self.chats)

		return conversations, conversations_description

	def get_features_emotions(self):
		emotions = {}
		emotions_description = {}

		emotions["emoji"] = {}
		emotions["emoticons"] = {}
		emotions_description["emoji"] = {}
		emotions_description["emoticons"] = {}

		emotions_description["emoji"]["happy"]     = "percentage of happy emoji     out of all the emoji"
		emotions_description["emoji"]["sad"]       = "percentage of sad   emoji     out of all the emoji"
		emotions_description["emoticons"]["happy"] = "percentage of happy emoticons out of all the emoticons"
		emotions_description["emoticons"]["sad"]   = "percentage of sad   emoticons out of all the emoticons"
		emotions["emoji"]["happy"]     = len(re.findall(
				utils.emoji.PATTERN_HAPPY,
				'\n'.join(self.messages_by_user_combined)
			)) / len(self.get_all_emojis())
		emotions["emoji"]["sad"]       = len(re.findall(
				utils.emoji.PATTERN_SAD,
				'\n'.join(self.messages_by_user_combined)
			)) / len(self.get_all_emojis())
		emotions["emoticons"]["happy"] = len(re.findall(
				utils.smily.PATTERN_HAPPY,
				'\n'.join(self.messages_by_user_combined)
			)) / len(self.get_all_emoticons())
		emotions["emoticons"]["sad"]   = len(re.findall(
				utils.smily.PATTERN_SAD,
				'\n'.join(self.messages_by_user_combined)
			)) / len(self.get_all_emoticons())

		return emotions, emotions_description

	def get_features(self, ret="dict"):
		ratio, ratio_description = self.get_features_ratio()
		laugh, laugh_description = self.get_features_laugh()
		active_hours, active_hours_description, \
		active_days, active_days_description = self.get_features_basic_time_statistics_general()
		activity = self.get_features_basic_time_statistics_per_user()
		conversations, conversations_description = self.get_features_conversations()
		emotions, emotions_description = self.get_features_emotions()

		if ret == "dict":
			return {
				"value" : {
					"ratio" : ratio,
					"laugh" : laugh,
					"active_hours" : active_hours,
					"active_days" : active_days,
					"activity" : activity,
					"conversations" : conversations,
					"emotions" : emotions,
				},
				"description" : {
					"ratio" : ratio_description,
					"laugh" : laugh_description,
					"active_hours" : active_hours_description,
					"active_days" : active_days_description,
					"conversations" : conversations_description,
					"emotions" : emotions_description,
				}
			}
		elif ret == "list":
			return [
				ratio["message"],
				ratio["media"],
				ratio["words"],
				ratio["long messages"],
				ratio["messages with h"],
				ratio["conversations"],
				*[	laugh["user%d hpm" % i]
					for i in range(len(self.users)) ],
				*[	laugh["user%d hpd" % i]
					for i in range(len(self.users)) ],
				*[	laugh["user%d h after media" % i]
					for i in range(len(self.users)) ],
				active_hours["07-12"],
				active_hours["12-17"],
				active_hours["17-21"],
				active_hours["21-07"],
				active_days["Sun"],
				active_days["Mon"],
				active_days["Tue"],
				active_days["Wed"],
				active_days["Thu"],
				active_days["Fri"],
				active_days["Sat"],
				*[	activity["user%d" % i]["day"]["message"]
					for i in range(len(self.users)) ],
				# activity["total"]["day"]["message"],
				*[	activity["user%d" % i]["day"]["media"]
					for i in range(len(self.users)) ],
				# activity["total"]["day"]["media"],
				*[	activity["user%d" % i]["day"]["words"]
					for i in range(len(self.users)) ],
				# activity["total"]["day"]["words"],
				*[	activity["user%d" % i]["day"]["emoji"]
					for i in range(len(self.users)) ],
				# activity["total"]["day"]["emoji"],
				*[	activity["user%d" % i]["day"]["emoticon"]
					for i in range(len(self.users)) ],
				# activity["total"]["day"]["emoticon"],
				*[	activity["user%d" % i]["message"]["emoji"]
					for i in range(len(self.users)) ],
				# activity["total"]["message"]["emoji"],
				*[	activity["user%d" % i]["message"]["emoticon"]
					for i in range(len(self.users)) ],
				# activity["total"]["message"]["emoticon"],
				conversations["week"],
				conversations["week 1<"],
				conversations["emotions"],
				conversations["avg diff time"],
				conversations["std diff time"],
				*[	conversations["user%d ignored chats" % i]
					for i in range(len(self.users)) ],
				*[	conversations["user%d avg between messages" % i]
					for i in range(len(self.users)) ],
				*[	conversations["user%d std between messages" % i]
					for i in range(len(self.users)) ],
				emotions["emoji"]["happy"],
				emotions["emoji"]["sad"],
				emotions["emoticons"]["happy"],
				emotions["emoticons"]["sad"],
			], [
				'ratio["message"]',
				'ratio["media"]',
				'ratio["words"]',
				'ratio["long messages"]',
				'ratio["messages with h"]',
				'ratio["conversations"]',
				*[	'laugh["user%d hpm"]' % i
					for i in range(len(self.users)) ],
				*[	'laugh["user%d hpd"]' % i
					for i in range(len(self.users)) ],
				*[	'laugh["user%d h after media"]' % i
					for i in range(len(self.users)) ],
				'active_hours["07-12"]',
				'active_hours["12-17"]',
				'active_hours["17-21"]',
				'active_hours["21-07"]',
				'active_days["Sun"]',
				'active_days["Mon"]',
				'active_days["Tue"]',
				'active_days["Wed"]',
				'active_days["Thu"]',
				'active_days["Fri"]',
				'active_days["Sat"]',
				*[	'activity["user%d"]["day"]["message"]' % i
					for i in range(len(self.users)) ],
				# 'activity["total"]["day"]["message"]',
				*[	'activity["user%d"]["day"]["media"]' % i
					for i in range(len(self.users)) ],
				# 'activity["total"]["day"]["media"]',
				*[	'activity["user%d"]["day"]["words"]' % i
					for i in range(len(self.users)) ],
				# 'activity["total"]["day"]["words"]',
				*[	'activity["user%d"]["day"]["emoji"]' % i
					for i in range(len(self.users)) ],
				# 'activity["total"]["day"]["emoji"]',
				*[	'activity["user%d"]["day"]["emoticons"]' % i
					for i in range(len(self.users)) ],
				# 'activity["total"]["day"]["emoticons"]',
				*[	'activity["user%d"]["message"]["emoji"]' % i
					for i in range(len(self.users)) ],
				# 'activity["total"]["message"]["emoji"]',
				*[	'activity["user%d"]["message"]["emoticons"]' % i
					for i in range(len(self.users)) ],
				# 'activity["total"]["message"]["emoticons"]',
				'conversations["week"]',
				'conversations["week 1<"]',
				'conversations["emotions"]',
				'conversations["avg diff time"]',
				'conversations["std diff time"]',
				*[	'conversations["user%d ignored chats"]' % i
					for i in range(len(self.users)) ],
				*[	'conversations["user%d avg between messages"]' % i
					for i in range(len(self.users)) ],
				*[	'conversations["user%d std between messages"]' % i
					for i in range(len(self.users)) ],
				'emotions["emoji"]["happy"]',
				'emotions["emoji"]["sad"]',
				'emotions["emoticons"]["happy"]',
				'emotions["emoticons"]["sad"]',
			]

	def print_features(self, **kwargs):
		l = self.get_features("list")
		print(", ".join(self.users), **kwargs)
		for i in list(zip(*l)):
			print("%-43s : %s" % i[::-1], **kwargs)

def print_line(x):
	print("%-6s - %s (%6.2f) - %s" % (
		x[1].split()[0],                 # sender
		x[0].strftime("%Y/%m/%d_%H:%M"), # date
		x[4].total_seconds() / 60**2,    # diff
		x[2][::-1]                       # message
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

def whos_the_funniest(data, plot=True, following_messages_amount=10):
	def is_media(x):
		return x[MI("TYPE")] == "MEDIA"
	def is_same_user(x,y):
		return x[MI("USER")] == y[MI("USER")]

	# get all the media messages
	all_media = data.get_following_messages(is_media, exclude_function=is_same_user, amount=following_messages_amount)

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
	input_file = [i[len("in:"   ):] for i in sys.argv[1:] if i.startswith("in:"   )]
	debug      = [i[len("debug:"):] for i in sys.argv[1:] if i.startswith("debug:")]
	dump       = [i[len("dump:" ):] for i in sys.argv[1:] if i.startswith("dump:" )]

	debug = int(debug[0]) if debug else True

	if input_file:
		d = Data(input_file[0], debug=debug)
	else:
		d = Data(               debug=debug)

	d.init_all(exclude_system=True)

	if dump:
		dump_file = dump[0]
		if dump_file:
			d.print_features(file=open(dump_file, time.strftime("data/w_%Y.%m.%d_%H:%M")))
		else:
			d.print_features()
	
else:
	d = Data(debug=True)
	d.init_all(exclude_system=True)
