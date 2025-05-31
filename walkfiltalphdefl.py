#!/usr/bin/python3

import os
import re


ALPHABET = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЪЫЭЮЯабвгдеёжзийклмнопрстуфхцчшщьъыэюя"
FILENAME_ENDINGS = [".txt.htm"]
IN_DIRPATH = "in"
IN_ENCODING = "cp1251"
OUT_DIRPATH = "out"
OUT_ENCODING = "utf8"
VERBOSE = True


def filtalphdefl(s):
	return re.sub("  +", " ", re.sub(f"[^{ALPHABET}]", " ", s))


def filtfilename(filename):
	for ending in FILENAME_ENDINGS:
		if filename.endswith(ending):
			return True
	return False


def walk(in_dipath=IN_DIRPATH, out_dirpath=OUT_DIRPATH, verbose=VERBOSE):
	try:
		os.mkdir(out_dirpath)
	except:
		pass
	n = 1
	for (root, dirnames, filenames) in os.walk(in_dirpath):
		for filename in filenames:
			if filtfilename(filename):
				with open(f"{root}/{filename}", "rb") as file:
					content = file.read().decode(IN_ENCODING, errors="replace")
				content = filtalphdefl(content)
				with open(f"{out_dirpath}/{n:05}_{filename}", "wb") as file:
					file.write(content.encode(OUT_ENCODING))
				if verbose:
					print(f"{n:05} : {filename}", flush=True)
				n += 1
	return (n - 1)


if __name__ == '__main__':
	count = walk()
	print(count)
