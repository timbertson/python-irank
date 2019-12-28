#!/usr/bin/env python3
import os, sys, re, time, dbus, gobject
from urllib import parse

from irank.core import fsenc

METADATA = 'Metadata'
URL_PROPERTY = 'xesam:url'

mpris_prefix="org.mpris.MediaPlayer2."
PLAYER = 'org.mpris.MediaPlayer2.Player'
mpris_object="/org/mpris/MediaPlayer2"

def init_glib():
	if not init_glib.called:
		init_glib.called = True
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)
init_glib.called = False

class Player(object):
	@classmethod
	def bus(cls):
		init_glib()
		return dbus.SessionBus()

	def __init__(self, name=None):
		init_glib()
		bus = dbus.SessionBus()
		self.player_name = name or os.environ.get('MPRIS_REMOTE_PLAYER', None) or type(self).guess_player_name()
		player_namespace = mpris_prefix + self.player_name
		player_obj = bus.get_object(player_namespace, mpris_object)

		self.player = dbus.Interface(player_obj, dbus_interface=PLAYER)
		self.properties = dbus.Interface(player_obj, dbus_interface=dbus.PROPERTIES_IFACE)

	@property
	def metadata(self):
		return self.properties.GetAll(PLAYER)[METADATA]

	@property
	def track(self):
		uri = self.metadata[URL_PROPERTY]
		try:
			return _path(uri)
		except ValueError:
			print("Invalid URI: %r" % (uri,))
			raise
	
	def next(self):
		self.player.Next();

	def each_track(self, cb):
		def playing_uri_changed(source, properties, signature):
			try:
				uri = properties[METADATA][URL_PROPERTY]
			except KeyError:
				return
			cb(_path(uri))

		self.properties.connect_to_signal('PropertiesChanged', playing_uri_changed)
		cb(self.track)
		loop = gobject.MainLoop()
		loop.run()
	
	def __repr__(self):
		return '<mpris.Player (%s)>' % (self.player_name,)

	@classmethod
	def possible_names(cls):
		return [ name[len(mpris_prefix):] for name in cls.bus().list_names() if name.startswith(mpris_prefix) ]

	# returns first matching player
	@classmethod
	def guess_player_name(cls):
		names = cls.possible_names()
		# print(repr(names))
		def score(name):
			# video players are usually not what we want
			if name in ('vlc', 'totem'):
				return 0
			# explicitly prefer music players
			if name in ('rhythmbox', 'banshee'):
				return 2
			return 1

		if not names:
			print("No MPRIS-compliant player found running.", file=sys.stderr)
			raise SystemExit(1)
		return max(names, key=score)

def _path(uri):
	# gobject gives us a unicode URL, which is cool.
	# But python2 decodes this into a _unicode_ string with _utf8_
	# byte sequences, like a right loon.
	#
	# However, if we give python a str (bytes) instead, it spits out a
	# str with those same utf-8 bytes, which will do. This may still be broken
	# if your FS uses something other than UTF-8, though.
	uri = uri.encode('ascii')
	# XXX python3 note: this hack should not be necessary, and will break

	transport, path = parse.splittype(uri)
	if transport != 'file':
		raise ValueError("%r type is not 'file'" % (transport,))
	return parse.unquote(path[2:]).decode('utf-8').encode(fsenc)


if __name__ == '__main__':
	def _(s):
		print(repr(s))
	player = Player()
	print("Monitoring track details from %s..." % (player.player_name,))
	try:
		player.each_track(_)
	except KeyboardInterrupt: pass
