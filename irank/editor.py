#!/usr/bin/env python

import re
import os
import sys
import readline

import logging

import irank

LIST_MODE = False

class SimpleCompleter(object):
	def __init__(self, options):
		self.options = options

	def complete(self, text, state):
		response = None
		if state == 0:
			if text:
				self.matches = [s for s in self.options if s and s.lower().startswith(text.lower())]
				logging.debug('%s matches: %s', repr(text), self.matches)
			else:
				self.matches = self.options[:]
				logging.debug('(empty input) matches: %s', self.matches)
			
			try:
				response = self.matches[state]
			except IndexError:
				response = None
			logging.debug('complete(%s, %s) => %s', repr(text), state, repr(response))
			return response

def init_rl():
	readline.set_completer(SimpleCompleter(irank.KEYS).complete)
	readline.parse_and_bind('tab: complete')


def main(*songs):
	for song in songs:
		print song
		song = irank.Song(song)
		print '-' * 30
		init_rl()

		if LIST_MODE:
			print song.values
			return

		modified = modify_ratings(song.values)
		if modified:
			print song.values.flatten()
			song.save()

def modify_ratings(values):
	changed = False
	try:
		while True:
			print
			print values
			print
			key = raw_input("change: ").strip()
			if not key: break
			key_parts = key.split()
			value = None
			if len(key_parts) > 1 and key_parts[-1].isdigit():
				value = key_parts.pop(-1)
				key = " ".join(key_parts)
			if not key in irank.KEYS:
				print "invalid key!"
				continue
			while True:
				try:
					if value is None:
						value = raw_input("   1-5: ").strip()
						if not value: break
					value = int(value)
					if value < 0 or value > 5:
						raise ValueError("must be between 1 and 5")
				except ValueError, e:
					value = None
					print e
					continue
				values[key] = value
				changed = True
				break
	except EOFError:
		pass
	return changed

