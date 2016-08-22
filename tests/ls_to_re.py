#!/usr/bin/env python3
import os
import utils

def ls(folder):
	# All the files in the folder
	directory_content = os.listdir(folder)
	directory_content = map(
		lambda x: x[:-4],
		directory_content
	)
	directory_content = list(directory_content)
	directory_content.sort()
	return directory_content

def main():
	data = ls("/home/me/Dropbox/Projects/Whatsapp/emoji/images")
	# data is sorted, so 1f3c3 will be before 1f3c3_1f3fb, thus I will not be able to catch it
	# re.findall("a|a1|a2|a3|a4|a5", "hello a4a4a2b4a1b5aa3") --> ['a', 'a', 'a', 'a', 'a', 'a']
	# re.findall("a5|a4|a3|a2|a1|a", "hello a4a4a2b4a1b5aa3") --> ['a4', 'a4', 'a2', 'a1', 'a', 'a3']
	data = data[::-1]
	data = map(
		lambda x: utils.re.escape(utils.emoji.hex_to_emoji(x)),
		data
	)
	return '|'.join(data)

def _test_regex():
	exec(open("tests/ls_to_re.py").read())
	# import tests.ls_to_re
	c_emoji = wp.d.get_messages(ls_to_re())
	c_non_letter = wp.d.get_messages('|'.join(wp.d._get_non_letters()))
	c_non_letter2 = wp.d.get_messages('|'.join(''.join(map(lambda x:x[2],wp.d.lines))))
	c_not_in_emoji = [i for i in c_non_letter if i not in c_emoji]
	c_not_in_non_letter = [i for i in c_emoji if i not in c_non_letter]

	print("c_emoji :", len(c_emoji))
	print("c_non_letter :", len(c_non_letter))
	print("c_not_in_emoji :", len(c_not_in_emoji))
	print("c_not_in_non_letter :", len(c_not_in_non_letter))

def test():
	directory_content = ls("/home/me/Dropbox/Projects/Whatsapp/emoji/images")
	first_char = get_first_char(directory_content)
	first_char_unique = list(set(first_char))

	a = list(zip(directory_content, map(get_emoji_type, get_first_char(directory_content))))
	def f(x):
		print(x.__repr__())
		return(" - ".join(x))
	b = list(map(f,a))

	single_char, multiple_char = single_multiple_char(directory_content)
	single_char_re, multiple_char_re = single_multiple_char_re(single_char, multiple_char)

if __name__ == '__main__':
	pattern = main()
else:
	test()