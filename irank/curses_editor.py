#!/usr/bin/env python

from tagpy import FileRef
import re
import os
import sys
import curses
from curses import ascii

import logging

import irank

LIST_MODE = False
A_STAR = None
A_KEY = None
A_FILENAME = None

NEXT = 1
PREVIOUS = -1
STAR = "*"

class Editor(object):
	def __init__(self, *songs):
		self.songs = songs
		self.lines = []
		self.selected_line = 0
		logging.basicConfig(level=logging.DEBUG, filename='/tmp/irank-editor-curses.log')
	
	def draw(self):
		self.win_height, self.win_width = self.scr.getmaxyx()
		self.scr.clear()
		self.draw_filename()
		self.draw_ratings()
		self.scr.refresh()
	
	def draw_filename(self):
		filename_start = min((self.win_width - len(self.filename)) / 4, 20)
		if filename_start < 0: filename_start = 0
		self.scr.insnstr(0, filename_start, self.filename, self.win_width, A_FILENAME)
	
	def draw_ratings(self):
		indent = 3
		y_start = 2
		margin = 1
		i = 0
		key_len = 15
		for key, rating in self.song.values.formatted_pairs():
			if self.selected_line == i:
				attr = curses.A_REVERSE
			else:
				attr = 0
			self.scr.insstr(i + y_start, indent, key, A_KEY | attr)
			self.scr.insstr(i + y_start, indent + margin + len(key), rating, A_STAR | attr)
			i += 1
		self.scr.move(self.selected_line + y_start, 0 + indent)


	def main(self, scr):
		self.init_colors()
		self.scr = scr
		for song in self.songs:
			self.filename = song
			self.selected_line = 0
			self.song = irank.Song(song)
			self.draw()
			logging.debug("editing song: %s" % (song,))

			def save():
				logging.debug("Saving file %s with comment: %s" % (
					self.filename, self.song.values.flatten()))
				self.song.save()

			while True:
				ch = self.scr.getch()
				if ch == ascii.NL:
					save()
					break
				elif ch == curses.KEY_UP:
					self.select(PREVIOUS)
				elif ch == curses.KEY_DOWN:
					self.select(NEXT)
				elif ch == curses.KEY_LEFT:
					self.add_rating(-1)
				elif ch == curses.KEY_RIGHT:
					self.add_rating(1)
				elif ch == curses.KEY_HOME:
					self.move_to(0)
				elif ch == curses.KEY_END:
					self.move_to(len(self.song.values)-1)
				elif ch == ascii.ESC:
					break
				elif ch == ascii.EOT: # ctrl-D
					return
				elif ascii.isprint(ch) and ascii.unctrl(ch) in "12345":
					self.set_rating(int(ascii.unctrl(ch)))
				elif ascii.isprint(ch) and ascii.unctrl(ch) == '`':
					self.set_rating(0)
				self.draw()

	def init_colors(self):
		global A_STAR, A_KEY, A_FILENAME
		curses.use_default_colors()
		curses.curs_set(2) # hide cursor

		n_star = 1
		n_key = 2
		n_filename = 3
		bg_index = -1

		curses.init_pair(n_filename, curses.COLOR_WHITE, bg_index)
		curses.init_pair(n_star, curses.COLOR_YELLOW, bg_index)
		curses.init_pair(n_key, curses.COLOR_WHITE, bg_index)

		A_FILENAME = curses.color_pair(n_filename)
		A_KEY = curses.color_pair(n_key) | curses.A_BOLD
		A_STAR = curses.color_pair(n_star)

	def move_to(self, index):
		self.selected_line = index
	
	def select(self, amount):
		self.selected_line += amount
		max_line = len(self.song.values) - 1
		if self.selected_line < 0: self.selected_line = 0
		if self.selected_line > max_line: self.selected_line = max_line
	
	def add_rating(self, amount):
		rating_key = self.song.values.keys()[self.selected_line]
		rating = self.song.values[rating_key]
		rating += amount
		if rating < 0: rating = 0
		if rating > 5: rating = 5
		self.song.values[rating_key] = rating
		logging.debug("set key %s to %s" % (rating_key, rating))
	
	def set_rating(self, rating):
		rating_key = self.song.values.keys()[self.selected_line]
		self.song.values[rating_key] = rating

def main(*args):
	curses.wrapper(Editor(*args).main)

