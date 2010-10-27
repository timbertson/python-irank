#!/usr/bin/env python
import os, sys, re, time, urllib2, dbus, gobject

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)
METADATA = 'Metadata'
URL_PROPERTY = 'xesam:url'

mpris_prefix="org.mpris.MediaPlayer2."
PLAYER = 'org.mpris.MediaPlayer2.Player'
mpris_object="/org/mpris/MediaPlayer2"

def possible_names():
	return [ name[len(mpris_prefix):] for name in bus.list_names() if name.startswith(mpris_prefix) ]

# returns first matching player
def get_player():
	names = possible_names()
	if not names:
		print >>sys.stderr, "No MPRIS-compliant player found running."
		raise SystemExit(1)
	return names[0]

def init():
	global bus, player_namespace, player, properties
	bus = dbus.SessionBus()
	player_name = os.environ.get('MPRIS_REMOTE_PLAYER', None) or get_player()
	player_namespace = mpris_prefix + player_name
	player_obj = bus.get_object(player_namespace, mpris_object)
	player = dbus.Interface(player_obj, dbus_interface=PLAYER)
	properties = dbus.Interface(player_obj, dbus_interface=dbus.PROPERTIES_IFACE)

def _path(uri):
	transport, path = urllib2.splittype(uri)
	if transport != 'file':
		raise ValueError("%r type is not 'file'" % (transport,))
	return urllib2.unquote(path[2:]).encode('utf-8')

def get_metadata():
	return properties.GetAll(PLAYER)[METADATA]

def current_file():
	uri = get_metadata()[URL_PROPERTY]
	try:
		return _path(uri)
	except ValueError:
		print "Invalid URI: %r" % (uri,)
		raise

def playing_songs(cb):
	def playing_uri_changed(source, properties, signature):
		try:
			uri = properties[METADATA][URL_PROPERTY]
		except KeyError:
			return
		cb(_path(uri))

	properties.connect_to_signal('PropertiesChanged', playing_uri_changed)
	cb(current_file())
	loop = gobject.MainLoop()
	loop.run()

if __name__ == '__main__':
	init()
	def _(s):
		print repr(s)
	playing_songs(_)
