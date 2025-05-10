#!/usr/bin/python3

import sounddevice
import soundfile

import curses
import glob
import os
import shutil
import time


DO_ERASE = True
IDLERATE = 100
REPLIQUES_DIRNAME = '_repliques_'
SPEAKER_FILENAME = 'speaker.txt'
SPEECH_FILENAME = 'speech.flac'
TEXT_FILENAME = 'text.txt'


def run(scr):
	scr.nodelay(True)
	if curses.can_change_color():
		curses.init_color(0, 0, 0, 0)
	curses.curs_set(0)
	scr.hline(curses.LINES - 2, 0, curses.ACS_HLINE, curses.COLS)
	scr.refresh()
	wnd_main = curses.newwin(curses.LINES - 2, curses.COLS, 0, 0)
	wnd_main.idlok(True) # seems to work even without this...
	wnd_main.scrollok(True)
	wnd_help = curses.newwin(1, curses.COLS, curses.LINES - 1, 0)
	wnd_help.idlok(True)
	wnd_help.scrollok(True)

	wnd_help.addstr('Q: quit | SPACE: next replique')
	wnd_help.refresh()	

	os.chdir(REPLIQUES_DIRNAME)
	dirnames = glob.glob('*')
	os.chdir('..')

	i = None
	for dirname in dirnames:
		try:
			n = int(dirname)
			i = n if (i is None) else min(i, n)
		except ValueError:
			pass
	if i is None:
		i = 1

	dirpath = f"{REPLIQUES_DIRNAME}/{i}"

	quit = False

	while not quit:
		
		if os.path.isdir(dirpath):
			with open(f"{dirpath}/{SPEAKER_FILENAME}", 'r') as file:
				speaker = file.read()
			with open(f"{dirpath}/{TEXT_FILENAME}", 'r') as file:
				text = file.read()
			speech, samplerate = soundfile.read(f"{dirpath}/{SPEECH_FILENAME}")

			wnd_main.addstr(f"[{i}] \"{speaker}\":\n\r{text}\n\r\n\r")
			wnd_main.refresh()

			sounddevice.play(speech, samplerate) # non-blocking
			stream = sounddevice.get_stream()

			status = 'PLAYING'
			wnd_help.addstr(0, curses.COLS - 1 - len(status), status)
			wnd_help.refresh()

			while stream.active:
				ch = scr.getch()
				if ch in {ord('q'), ord('Q')}:
					stream.stop()
					quit = True
					break
				elif ch == ord(' '):
					stream.stop()
					break
				time.sleep(1.0 / IDLERATE) # prevents CPU overusage

			if DO_ERASE:
				shutil.rmtree(dirpath)

			i += 1
			dirpath = f"{REPLIQUES_DIRNAME}/{i}"

		else:
			status = 'WAITING'
			wnd_help.addstr(0, curses.COLS - 1 - len(status), status)
			wnd_help.refresh()

		if scr.getch() in {ord('q'), ord('Q')}:
			quit = True

		time.sleep(1.0 / IDLERATE) # prevents CPU overusage


if __name__ == '__main__':
	curses.wrapper(run)
