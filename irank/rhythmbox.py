import dbus
import urllib2
import gobject

from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

bus = dbus.SessionBus()
rbplayerobj = bus.get_object('org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Player')
rbplayer = dbus.Interface(rbplayerobj, 'org.gnome.Rhythmbox.Player')


def _path(uri):
	transport, path = urllib2.splittype(uri)
	if transport != 'file':
		raise ValueError("%r type is not 'file'" % (transport,))
	return urllib2.unquote(path[2:]).encode('utf-8')

def current_file():
	uri = rbplayer.getPlayingUri()
	try:
		return _path(uri)
	except ValueError:
		print "Invalid URI: %r" % (uri,)
		raise

def playing_songs(cb):
	rbshellobj = bus.get_object('org.gnome.Rhythmbox', '/org/gnome/Rhythmbox/Shell')
	rbshell = dbus.Interface(rbshellobj, 'org.gnome.Rhythmbox.Shell')
	def playing_uri_changed(uri):
		cb(_path(uri))

	rbplayer.connect_to_signal('playingUriChanged', playing_uri_changed)
	try:
		cb(current_file())
	except ValueError: pass
	loop = gobject.MainLoop()
	loop.run()
