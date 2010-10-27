#!/usr/bin/env python
import os, sys, re, time, urllib2, dbus, gobject

METADATA = 'Metadata'
URL_PROPERTY = 'xesam:url'

mpris_prefix="org.mpris.MediaPlayer2."
PLAYER = 'org.mpris.MediaPlayer2.Player'
mpris_object="/org/mpris/MediaPlayer2"

def init_glib():
	from dbus.mainloop.glib import DBusGMainLoop
	DBusGMainLoop(set_as_default=True)

class Player(object):
	instance = None
	def __new__(cls, name=None):
		if cls.instance is None:
			init_glib()
			instance = super(type(cls), cls).__new__(cls)
			bus = dbus.SessionBus()
			player_name = name or os.environ.get('MPRIS_REMOTE_PLAYER', None) or guess_player_name(bus)
			player_namespace = mpris_prefix + player_name
			player_obj = bus.get_object(player_namespace, mpris_object)

			instance.player = dbus.Interface(player_obj, dbus_interface=PLAYER)
			instance.properties = dbus.Interface(player_obj, dbus_interface=dbus.PROPERTIES_IFACE)
			cls.instance = instance
		return cls.instance

	@property
	def metadata(self):
		return self.properties.GetAll(PLAYER)[METADATA]

	@property
	def track(self):
		uri = self.metadata[URL_PROPERTY]
		try:
			return _path(uri)
		except ValueError:
			print "Invalid URI: %r" % (uri,)
			raise

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


def possible_names(bus):
	return [ name[len(mpris_prefix):] for name in bus.list_names() if name.startswith(mpris_prefix) ]

# returns first matching player
def guess_player_name(bus):
	names = possible_names(bus)
	if not names:
		print >>sys.stderr, "No MPRIS-compliant player found running."
		raise SystemExit(1)
	return names[0]

def _path(uri):
	transport, path = urllib2.splittype(uri)
	if transport != 'file':
		raise ValueError("%r type is not 'file'" % (transport,))
	return urllib2.unquote(path[2:]).encode('utf-8')


if __name__ == '__main__':
	def _(s):
		print repr(s)
	Player().each_track(_)
